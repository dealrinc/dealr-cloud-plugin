#!/usr/bin/env python3
"""Select an automatic version delivery only when main advances its version."""

import json
import os
from pathlib import Path
import re
import subprocess


def decide(version, previous, tag_exists):
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("A stable semantic version is required")
    if previous is not None and (not isinstance(previous, str) or not re.fullmatch(r"\d+\.\d+\.\d+", previous)):
        raise ValueError("Previous package version is invalid")
    changed = previous != version
    if changed and previous and tuple(map(int, version.split("."))) <= tuple(map(int, previous.split("."))):
        raise ValueError("Package version must increase")
    if changed and tag_exists:
        raise ValueError("This version tag already exists; choose a new version")
    return "v" + version, changed


def main():
    subprocess.run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], check=True)
    version = json.loads(Path("plugin-source.json").read_text())["version"]
    parent = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "HEAD^"], capture_output=True)
    previous = None
    if parent.returncode == 0:
        paths = subprocess.check_output(["git", "ls-tree", "--name-only", "HEAD^", "plugin-source.json"], text=True)
        if paths.strip():
            previous = json.loads(subprocess.check_output(["git", "show", "HEAD^:plugin-source.json"], text=True))["version"]
    # Validate the version before using it to form a ref or a workflow output.
    tag, _ = decide(version, previous, False)
    exists = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "refs/tags/" + tag], capture_output=True)
    tag, changed = decide(version, previous, exists.returncode == 0)
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write("publish=" + str(changed).lower() + "\n")
        output.write("tag=" + tag + "\n")


if __name__ == "__main__":
    main()
