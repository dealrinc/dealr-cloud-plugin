#!/usr/bin/env python3
"""Verify built artifacts and prepare GitHub assets plus platform handoff notes."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile

import plugin

ROOT = Path(__file__).resolve().parents[1]


def prepare(tag, commit):
    data = plugin.source()
    plugin.require(tag == "v" + data["version"], "Tag must match the package version exactly")
    plugin.require(re.fullmatch(r"[0-9a-f]{40}", commit), "A full Git commit SHA is required")
    plugin.check(data)
    chatgpt = plugin.chatgpt_metadata(data)
    chatgpt_manifest = json.loads(chatgpt[".codex-plugin/plugin.json"])
    expected = {
        "shared": (data["name"], ".claude-plugin/plugin.json", plugin.generated(data)[".claude-plugin/plugin.json"]),
        "chatgpt": (chatgpt_manifest["name"], ".codex-plugin/plugin.json", chatgpt_manifest),
    }
    verified = []
    for target, (name, manifest_path, metadata) in expected.items():
        folder = ROOT / "dist" / target
        archive = folder / f"{name}-{data['version']}.zip"
        plugin.require(sorted(folder.glob("*.zip")) == [archive], f"Expected exactly the current {target} archive")
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        plugin.require((folder / "SHA256SUMS").read_text() == f"{digest}  {archive.name}\n",
                       f"Checksum mismatch for {target}")
        with zipfile.ZipFile(archive) as bundle:
            plugin.require(json.loads(bundle.read(manifest_path)) == metadata, f"Wrong metadata in {target} archive")
            connection = json.loads(bundle.read(".mcp.json"))
            expected_connection = (json.loads(chatgpt[".mcp.json"]) if target == "chatgpt"
                                   else plugin.generated(data)[".mcp.json"])
            plugin.require(connection == expected_connection, f"Wrong connection in {target} archive")
        verified.append({"target": target, "file": archive.name, "sha256": digest,
                         "bytes": archive.stat().st_size, "packageName": name})

    destination = ROOT / "delivery"
    destination.mkdir(exist_ok=True)
    plugin.require(not list(destination.glob("*.zip")), "Delivery directory already has archives; start from a clean directory")
    for item in verified:
        shutil.copyfile(ROOT / "dist" / item["target"] / item["file"], destination / item["file"])
    (destination / "SHA256SUMS").write_text("".join(f"{item['sha256']}  {item['file']}\n" for item in verified))
    (destination / "manifest.json").write_text(plugin.text({
        "version": data["version"], "tag": tag, "commit": commit, "artifacts": verified,
        "marketplacePublication": "Separate from this GitHub publication; see handoff notes",
    }))
    notes = f"""# Dealr.cloud {tag}

Commit: {commit}

{data['openai']['updateNotes']}

Both archives were built and validated from this tagged commit. The attached
SHA256SUMS verifies the exact downloadable ZIP filenames; manifest.json records
their target, package identity, size, and digest. This GitHub publication does
not establish authenticated runtime testing or marketplace approval.

## Platform handoff

- Claude: confirm the directory tracks the intended branch/tag and has its
  GitHub webhook configured. Check the scan and publish state at
  https://claude.ai/directory/manage. Auto-publication depends on Anthropic's
  setting for the listing; this workflow does not configure it.
- Cursor: request review of this version at
  https://cursor.com/marketplace/publish. Public marketplace updates require
  Cursor review. Team marketplace Auto Refresh is configured separately.
  Cursor's public guidance requires open-source plugins; resolve the current
  proprietary-license eligibility with Cursor before public publication.
- ChatGPT: upload the app-named ZIP to the existing Dealr.cloud plugin at
  https://platform.openai.com/plugins. Verify imported metadata and the existing
  OAuth connection, complete applicable scans/review, and publish the approved
  version. Do not create a duplicate app. Reviewer credentials stay in the
  portal, never in GitHub assets.

No platform credentials or undocumented publishing APIs are used by this workflow.
"""
    (destination / "NOTES.md").write_text(notes)
    print(f"Prepared {len(verified)} verified artifacts in {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    try:
        prepare(args.tag, args.commit)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
