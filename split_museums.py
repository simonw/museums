#!/usr/bin/env python3
"""
Split museums.yaml into individual museums/{id}.yaml files,
recreating git edit history based on when each museum entry
was created and modified in the original museums.yaml.

This script:
1. Walks through all commits that touched museums.yaml (chronologically)
2. For each commit, determines which museums were added or changed
3. Writes the individual museums/{id}.yaml files
4. Creates git commits preserving the original timestamps and messages

Usage:
    python split_museums.py [--dry-run]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import git
import yaml


def iterate_file_versions(repo_path, filepath, ref="main"):
    """Yield (datetime, hexsha, message, content) for each commit that touched filepath."""
    repo = git.Repo(repo_path, odbt=git.GitDB)
    commits = reversed(list(repo.iter_commits(ref, paths=filepath)))
    for commit in commits:
        try:
            blob = [b for b in commit.tree.blobs if b.name == filepath][0]
        except IndexError:
            continue
        yield commit.committed_datetime, commit.hexsha, commit.message.strip(), blob.data_stream.read()


def museum_to_yaml(museum):
    """Serialize a single museum dict to YAML string."""

    class IndentDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super().increase_indent(flow, False)

    return yaml.dump(
        museum,
        Dumper=IndentDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )


def museums_match(a, b):
    """Compare two museum dicts for equality."""
    return json.dumps(a, sort_keys=True, default=str) == json.dumps(
        b, sort_keys=True, default=str
    )


def run_git(args, env=None):
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        print(f"  git {' '.join(args)} failed: {result.stderr}", file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description="Split museums.yaml into individual files with history")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--ref", default="HEAD", help="Git ref to read history from (default: HEAD)")
    args = parser.parse_args()

    repo_path = "."
    museums_dir = Path("museums")

    if not args.dry_run:
        museums_dir.mkdir(exist_ok=True)

    print("Walking git history of museums.yaml...")
    previous = {}
    commits_made = 0

    for when, hexsha, message, content in iterate_file_versions(repo_path, "museums.yaml", args.ref):
        try:
            current = {m["id"]: m for m in yaml.safe_load(content)}
        except (yaml.scanner.ScannerError, yaml.parser.ParserError):
            print(f"  Skipping {hexsha[:7]} - invalid YAML")
            continue

        # Find added museums
        added_ids = [id for id in current if id not in previous]
        # Find changed museums
        changed_ids = [
            id for id in current
            if id in previous and not museums_match(current[id], previous[id])
        ]
        # Find removed museums
        removed_ids = [id for id in previous if id not in current]

        affected_ids = added_ids + changed_ids
        if not affected_ids and not removed_ids:
            previous = current
            continue

        if args.dry_run:
            print(f"  {hexsha[:7]} ({when.isoformat()}) - {message[:60]}")
            if added_ids:
                print(f"    Added: {added_ids}")
            if changed_ids:
                print(f"    Changed: {changed_ids}")
            if removed_ids:
                print(f"    Removed: {removed_ids}")
            previous = current
            continue

        # Write affected museum files
        files_to_stage = []
        for museum_id in affected_ids:
            museum = current[museum_id]
            filepath = museums_dir / f"{museum_id}.yaml"
            yaml_content = museum_to_yaml(museum)
            filepath.write_text(yaml_content)
            files_to_stage.append(str(filepath))

        # Remove deleted museum files
        for museum_id in removed_ids:
            filepath = museums_dir / f"{museum_id}.yaml"
            if filepath.exists():
                filepath.unlink()
                files_to_stage.append(str(filepath))

        if files_to_stage:
            # Stage files
            run_git(["add"] + files_to_stage)

            # Commit with original timestamp
            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = when.isoformat()
            env["GIT_COMMITTER_DATE"] = when.isoformat()

            # Build a descriptive commit message
            parts = []
            if added_ids:
                names = [current[id]["name"] for id in added_ids]
                parts.append(f"Add: {', '.join(names)}")
            if changed_ids:
                names = [current[id]["name"] for id in changed_ids]
                parts.append(f"Update: {', '.join(names)}")
            if removed_ids:
                names = [previous[id]["name"] for id in removed_ids]
                parts.append(f"Remove: {', '.join(names)}")

            commit_msg = f"[split] {'; '.join(parts)}\n\nOriginal commit: {hexsha[:7]} - {message}"

            result = run_git(["commit", "-m", commit_msg], env=env)
            if result.returncode == 0:
                commits_made += 1
                print(f"  Commit {commits_made}: {hexsha[:7]} -> {'; '.join(parts)}")
            else:
                print(f"  Skipped (nothing to commit): {hexsha[:7]}")

        previous = current

    if args.dry_run:
        print(f"\nDry run complete. Would process {len(previous)} museums.")
    else:
        print(f"\nDone! Created {commits_made} commits for {len(previous)} museums.")
        print(f"Museum files are in {museums_dir}/")


if __name__ == "__main__":
    main()
