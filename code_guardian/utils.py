from pathlib import Path

from code_guardian.models import RepoOutcome


def report_name(outcome: RepoOutcome) -> str:
    repo = outcome.repo
    if repo.owner and repo.name:
        return f"{repo.owner}-{repo.name}"
    return Path(repo.url).name
