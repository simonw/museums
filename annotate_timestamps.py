import git
import sqlite_utils
from pathlib import Path
from sqlite_utils.db import NotFoundError


def get_file_timestamps(repo_path, filepath, ref="main"):
    """Return (created, updated) datetimes for a file based on git history."""
    repo = git.Repo(repo_path, odbt=git.GitDB)
    commits = list(repo.iter_commits(ref, paths=filepath))
    if not commits:
        return None, None
    # commits are newest-first
    created = commits[-1].committed_datetime
    updated = commits[0].committed_datetime
    return created, updated


if __name__ == "__main__":
    ref = "HEAD"
    museums_dir = Path("museums")
    db = sqlite_utils.Database("browse.db")

    for path in sorted(museums_dir.glob("*.yaml"), key=lambda p: int(p.stem)):
        museum_id = int(path.stem)
        created, updated = get_file_timestamps(".", str(path), ref)
        if created is None:
            continue
        try:
            db["museums"].update(
                museum_id,
                {"created": created.isoformat(), "updated": updated.isoformat()},
                alter=True,
            )
        except NotFoundError:
            pass
