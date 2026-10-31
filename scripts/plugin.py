#!/usr/bin/env python3
"""Generate host metadata, check the bundle, and build a reproducible upload ZIP."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ("name", "version", "description", "author", "homepage", "repository", "license", "keywords")
LISTING = ("icon", "documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_path(value):
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts, f"Unsafe path: {value}")
    result = ROOT / path
    require(result.exists() and result.resolve().is_relative_to(ROOT), f"Missing or external path: {value}")
    require(not any(part.is_symlink() for part in (result, *result.parents) if part != ROOT and ROOT in part.parents),
            f"Symlink not allowed: {value}")
    return result


def https_url(value, field):
    require(isinstance(value, str) and not any(char.isspace() for char in value), f"{field}: invalid URL")
    parsed = urlsplit(value)
    require(parsed.scheme == "https" and parsed.hostname, f"{field}: use an absolute HTTPS URL")
    require(parsed.username is None and parsed.password is None, f"{field}: embedded credentials are not allowed")
    require(not parsed.query and not parsed.fragment, f"{field}: query strings and fragments are not allowed")
    parsed.port


def source():
    data = json.loads((ROOT / "plugin-source.json").read_text())
    expected = set(CORE + LISTING + ("displayName", "marketplaceName", "servers", "openai"))
    require(set(data) == expected, "plugin-source.json has missing or unknown fields")
    for field in ("name", "marketplaceName"):
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data[field]) and len(data[field]) <= 64,
                f"Invalid {field}")
    require(re.fullmatch(r"\d+\.\d+\.\d+", data["version"]), "Use a stable semantic version")
    require(data["description"] and data["author"].get("name"), "Description and author are required")
    for field in ("homepage", "repository") + LISTING[1:]:
        https_url(data[field], field)
    if "url" in data["author"]:
        https_url(data["author"]["url"], "author.url")
    require(data["servers"], "At least one MCP server is required")
    for name, server in data["servers"].items():
        require(set(server) == {"type", "url"}, f"{name}: hosted OAuth config must contain only type and url")
        require(server["type"] == "http", f"{name}: use HTTP transport")
        https_url(server["url"], f"{name} MCP endpoint")
    local_path(data["icon"])
    return data


def generated(data):
    core = {key: data[key] for key in CORE}
    claude = {**core, "displayName": data["displayName"], **{key: data[key] for key in LISTING}}
    cursor = {**core, "logo": data["icon"], "skills": "./skills/", "mcpServers": "./mcp.json"}
    marketplace = {
        "name": data["marketplaceName"], "owner": {"name": data["author"]["name"]},
        "metadata": {"description": data["description"]},
        "plugins": [{"name": data["name"], "source": "./", "description": data["description"]}],
    }
    mcp = {"mcpServers": data["servers"]}
    return {
        ".claude-plugin/plugin.json": claude,
        ".claude-plugin/marketplace.json": marketplace,
        ".cursor-plugin/plugin.json": cursor,
        ".cursor-plugin/marketplace.json": marketplace,
        ".mcp.json": mcp,
        "mcp.json": mcp,
    }


def text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def bundle_files():
    files = [ROOT / "README.md", ROOT / "LICENSE"]
    files += [ROOT / p for p in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json", ".mcp.json", "mcp.json")]
    for directory in ("skills", "assets", "docs"):
        folder = local_path(directory)
        entries = list(folder.rglob("*"))
        for entry in entries:
            require(not entry.is_symlink(), f"Symlink not allowed: {entry.relative_to(ROOT)}")
        files += [p for p in entries if p.is_file()]
    return sorted(files)


def check(data):
    files = bundle_files()
    for path, value in generated(data).items():
        require((ROOT / path).is_file() and (ROOT / path).read_text() == text(value),
                f"Generated file is stale: {path}; run python3 scripts/plugin.py sync")
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    require(skills, "No skills found")
    names = set()
    for skill in skills:
        body = skill.read_text()
        match = re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n", body)
        require(match is not None, f"{skill}: expected simple name/description YAML frontmatter")
        name, description = match.groups()
        require(name == skill.parent.name and name not in names and len(name) <= 64, f"Invalid or duplicate skill: {name}")
        require(description.strip() and "<" not in description and ">" not in description,
                f"Invalid skill description: {name}")
        names.add(name)
    require(set(skills).issubset(files), "A discovered skill is missing from the bundle")
    require(len(files) <= 512, "Bundle exceeds directory file limit")
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        local_path(relative)
        require(path.stat().st_size < 5 * 1024 * 1024, f"File too large: {relative}")
        require(path.suffix in {".png", ".svg", ".json", ".md"} or path.name == "LICENSE", f"Unexpected bundle file: {relative}")
        if path.suffix != ".png":
            require(path.stat().st_size < 256 * 1024, f"Text file too large: {relative}")
            content = path.read_text()
            require(not re.search(r"gh[pousr]_[A-Za-z0-9]{20,}|sk-proj-|-----BEGIN .*PRIVATE KEY-----", content),
                    f"Possible credential in {relative}")
    require(len((ROOT / "README.md").read_text().split()) >= 40, "README is too short")
    require((ROOT / "LICENSE").read_text().strip(), "License is missing")
    png = local_path(data["icon"]).read_bytes()
    require(png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (512, 512), "Icon must be a 512px square PNG")
    svg = ET.parse(ROOT / "assets/logo.svg").getroot()
    require(svg.attrib.get("viewBox") == "0 0 512 512", "SVG must be square")
    rect = svg.find("{http://www.w3.org/2000/svg}rect")
    require(rect is not None and rect.attrib.get("width") == "512" and rect.attrib.get("height") == "512"
            and rect.attrib.get("fill", "none") != "none" and rect.attrib.get("opacity", "1") == "1", "SVG needs an opaque background")
    print(f"Validated Claude and Cursor metadata, OAuth transport, {len(skills)} skills, and {len(files)} bundle files")


def chatgpt_metadata(data):
    settings = data["openai"]
    require(set(settings) == {"baseline", "asset", "updateNotes"}, "Missing or unknown OpenAI export settings")
    baseline = json.loads(local_path(settings["baseline"]).read_text())
    require(set(baseline) == {"manifest", "mcp"}, "Invalid ChatGPT baseline envelope")
    manifest, mcp = baseline["manifest"], baseline["mcp"]

    def inspect(value):
        if isinstance(value, dict):
            require(not set(value).intersection({"clientSecret", "test_credentials", "reviewer_instructions", "password"}),
                    "Private credentials or reviewer access must not be packaged")
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
    inspect(baseline)
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest["name"]), "Invalid existing ChatGPT package identity")
    require(manifest["skills"] == "./skills/" and manifest["mcpServers"] == "./.mcp.json",
            "Unsupported ChatGPT component paths")
    require(not set(manifest).intersection({"apps", "hooks"}), "App references and hooks are not supported by this export")
    interface = manifest["interface"]
    for field, limit in [("displayName", 30), ("shortDescription", 30), ("longDescription", 4000), ("developerName", 80)]:
        value = interface[field]
        require(isinstance(value, str) and 0 < len(value) <= limit, f"OpenAI {field}: invalid length")
    for field in ["websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"]:
        https_url(interface[field], f"OpenAI {field}")
    for field in ["brandColor", "brandColorDark"]:
        require(re.fullmatch(r"#[0-9a-fA-F]{6}", interface[field]), f"Invalid OpenAI {field}")
    prompts = interface["defaultPrompt"]
    require(isinstance(prompts, list) and len(prompts) <= 3 and all(isinstance(p, str) and 0 < len(p) <= 128 for p in prompts),
            "Invalid OpenAI starter prompts")
    require(len(mcp["mcpServers"]) == len(data["servers"]) == 1, "ChatGPT export supports exactly one MCP server")
    for server in mcp["mcpServers"].values():
        require(set(server) == {"url"}, "Baseline connection must remain URL-only; change authentication explicitly")
        https_url(server["url"], "ChatGPT MCP endpoint")
        require(server["url"] == next(iter(data["servers"].values()))["url"], "ChatGPT and shared MCP endpoints differ")
    extensions = manifest["extensions"]["com.openai"]
    require(not set(extensions).intersection({"apps", "hooks"}), "OpenAI app references and hooks are not supported")
    onboarding = local_path(extensions["onboardingSkill"])
    require(onboarding in bundle_files() and onboarding.name == "SKILL.md" and ROOT / "skills" in onboarding.parents,
            "OpenAI onboarding skill must be a bundled skill")
    review = extensions["review"]
    cases = review["test_cases"]
    require(len(cases["positive"]) == 5 and len(cases["negative"]) == 3, "Retain five positive and three negative cases")
    for case in cases["positive"]:
        require(all(isinstance(case.get(k), str) and case[k].strip() for k in
                    ["description", "prompt", "tools_triggered", "expected_behavior"]), "Incomplete positive review case")
    for case in cases["negative"]:
        require(all(isinstance(case.get(k), str) and case[k].strip() for k in ["description", "prompt"]),
                "Incomplete negative review case")
    https_url(review["demo_recording_url"], "Review demo URL")
    require(settings["updateNotes"].strip(), "ChatGPT update notes are required")
    require(tuple(map(int, data["version"].split("."))) > tuple(map(int, manifest["version"].split("."))),
            "The exported version must be newer than the baseline")
    manifest["version"] = data["version"]
    extensions["publication"]["release_notes"] = settings["updateNotes"]
    return {".codex-plugin/plugin.json": text(manifest), ".mcp.json": text(mcp)}


def chatgpt_assets(data, manifest):
    image = local_path(data["openai"]["asset"]).read_bytes()
    require(image[:8] == bytes.fromhex("89504e470d0a1a0a"), "ChatGPT asset must be a PNG")
    width, height = struct.unpack(">II", image[16:24])
    require(width == height and 48 <= width <= 4096, "ChatGPT icon must be square and between 48 and 4096 pixels")
    output = {}
    for key in ("logo", "logoDark", "composerIcon", "composerIconDark"):
        path = manifest["interface"].get(key)
        if path:
            name = PurePosixPath(path)
            require(path.startswith("./assets/") and ".." not in name.parts and name.suffix == ".png",
                    f"Invalid OpenAI asset path: {path}")
            output[name.as_posix()] = image
    require("logo" in manifest["interface"] and "composerIcon" in manifest["interface"], "ChatGPT icons are required")
    return output


def build(data, target="shared"):
    check(data)
    replacements = chatgpt_metadata(data) if target == "chatgpt" else {}
    exported = json.loads(replacements[".codex-plugin/plugin.json"]) if replacements else data
    output = ROOT / "dist" / target
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{exported['name']}-{exported['version']}.zip"
    contents = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in bundle_files()}
    if target == "chatgpt":
        contents = {name: content for name, content in contents.items()
                    if name == "LICENSE" or name.startswith("skills/")}
        contents.update(chatgpt_assets(data, exported))
        contents["README.md"] = (
            f"# {exported['interface']['displayName']}\n\n{exported['interface']['longDescription']}\n\n"
            "This is an OpenAI/Codex-compatible export with shared Dealr skills, branding, and a remote OAuth connection. "
            "Import it as an MCP-enabled plugin. Update the existing Dealr.cloud plugin identity where applicable. "
            "Local packaging checks do not prove OpenAI importer acceptance or an authenticated connection. "
            "Complete domain verification, OAuth and identity checks, skill/tool scans, and reviewer testing before submission. "
            "Reviewer credentials must be entered privately in the portal, never in this package.\n\n"
            f"Privacy policy: {exported['interface']['privacyPolicyURL']}\n\nTerms: {exported['interface']['termsOfServiceURL']}\n\n"
            f"Support: {exported['interface']['supportURL']}\n\nSee LICENSE for proprietary rights.\n"
        ).encode()
        contents.update({name: content.encode() for name, content in replacements.items()})
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, content in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, content)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{digest}  {archive.name}\n")
    print(f"Built {archive.relative_to(ROOT)}\nSHA256 {digest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sync", "check", "build"))
    parser.add_argument("--target", choices=("shared", "chatgpt"), default="shared")
    args = parser.parse_args()
    data = source()
    if args.command == "sync":
        for path, value in generated(data).items():
            destination = ROOT / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text(value))
        print("Generated Claude and Cursor manifests, marketplace indexes, and MCP configs")
    elif args.command == "check":
        check(data)
    else:
        build(data, args.target)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
