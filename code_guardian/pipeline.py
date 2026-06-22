import shutil
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from code_guardian.adapters.cloner import GitCloner
from code_guardian.adapters.github import GitHubClient
from code_guardian.errors import CloneError
from code_guardian.models import RepoOutcome, RepoPopularity, RepoSpec


@asynccontextmanager
async def workspace() -> AsyncGenerator[Path, None]:
    path = Path(tempfile.mkdtemp(prefix="cg-"))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


async def process_repository(
    repo: RepoSpec, *, cloner: GitCloner, github: GitHubClient
) -> RepoOutcome:
    if repo.is_local:
        return await _process(repo, path=Path(repo.url), github=github)

    async with workspace() as ws:
        try:
            await cloner.clone(repo.url, ws)
        except CloneError as exc:
            return RepoOutcome(repo=repo, success=False, error=exc)
        return await _process(repo, path=ws, github=github)


async def _process(repo: RepoSpec, *, path: Path, github: GitHubClient) -> RepoOutcome:
    if repo.owner and repo.name:
        popularity = await github.get_popularity(repo.owner, repo.name)
    else:
        popularity = RepoPopularity.unknown()
    return RepoOutcome(repo=repo, success=True, popularity=popularity)
