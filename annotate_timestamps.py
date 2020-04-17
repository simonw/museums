import git
import yaml
import json
import sqlite_utils


IGNORE_CHANGES_IN_COMMITS = {
    # This commit updated all existing press dates to a new format
    "78fa0ac54dcaa9c52e8962a44b574b082bc726d3"
}


def iterate_file_versions(repo_path, filepath, ref="master"):
    repo = git.Repo(repo_path, odbt=git.GitDB)
    commits = reversed(list(repo.iter_commits(ref, paths=filepath)))
    for commit in commits:
        blob = [b for b in commit.tree.blobs if b.name == filepath][0]
        yield commit.committed_datetime, commit.hexsha, blob.data_stream.read()


if __name__ == "__main__":
    ref = "master"
    it = iterate_file_versions(".", "museums.yaml", ref)
    previous = {}
    created = {}
    updated = {}
    for when, hash, content in it:
        try:
            current = {m["id"]: m for m in yaml.safe_load(content)}
        except (yaml.scanner.ScannerError, yaml.parser.ParserError):
            # This must have been invalid YAML - skip
            continue
        # First detect the new museums
        added_ids = [id for id in current if id not in previous]
        for id in added_ids:
            created[id] = when.isoformat()
            updated[id] = when.isoformat()
        # Now detect those that have changed since prev
        if hash not in IGNORE_CHANGES_IN_COMMITS:
            changed_ids = [
                id
                for id in current
                if json.dumps(current[id], sort_keys=True, default=str)
                != json.dumps(previous.get(id, {}), sort_keys=True, default=str)
            ]
            for id in changed_ids:
                updated[id] = when.isoformat()
        previous = current
    print("Created:")
    print(json.dumps(created, indent=4))
    print("Updated:")
    print(json.dumps(updated, indent=4))
    db = sqlite_utils.Database("browse.db")
    for id, ts in created.items():
        db["museums"].update(id, {"created": ts, "updated": updated[id]}, alter=True)
