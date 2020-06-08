import os

import pygit2


def get_last_commit_id(repo_path: str) -> str:
    repo_path = os.path.expandvars(repo_path)
    repo = pygit2.Repository(repo_path)
    return str(repo.head.target)


def clone(repo_path: str, clone_path: str, commit_id: str):
    repo_path = os.path.expandvars(repo_path)
    pygit2.clone_repository(repo_path, clone_path)
    repo = pygit2.Repository(clone_path)
    repo.set_head(pygit2.Oid(hex=commit_id))
