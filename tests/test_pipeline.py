from pathlib import Path

import pytest

from code_guardian.errors import CloneError
from code_guardian.models import RepoPopularity, RepoSpec
from code_guardian.pipeline import process_repository


class FakeCloner:
    async def clone(self, url: str, dest: Path) -> None:
        pass


class FailingCloner:
    async def clone(self, url: str, dest: Path) -> None:
        raise CloneError("repository not found")


class FakeGitHub:
    async def get_popularity(self, owner: str, repo: str) -> RepoPopularity:
        return RepoPopularity(stars=100, forks=50)


async def test_remote_repo_success():
    spec = RepoSpec.from_url("https://github.com/OWASP/NodeGoat")
    outcome = await process_repository(spec, cloner=FakeCloner(), github=FakeGitHub())
    assert outcome.success
    assert outcome.popularity is not None
    assert outcome.popularity.stars == 100


async def test_clone_failure_returns_failed_outcome():
    spec = RepoSpec.from_url("https://github.com/OWASP/NodeGoat")
    outcome = await process_repository(spec, cloner=FailingCloner(), github=FakeGitHub())
    assert not outcome.success
    assert isinstance(outcome.error, CloneError)


async def test_local_repo_skips_clone():
    spec = RepoSpec.from_url("/some/local/path")
    outcome = await process_repository(spec, cloner=FailingCloner(), github=FakeGitHub())
    assert outcome.success
    assert outcome.popularity == RepoPopularity.unknown()
