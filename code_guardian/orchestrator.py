import asyncio
import logging

from code_guardian.pipeline import Cloner, GitHub, Scanner, process_repository
from code_guardian.models import RepoOutcome, RepoSpec

log = logging.getLogger(__name__)


async def run(
    specs: list[RepoSpec],
    *,
    cloner: Cloner,
    github: GitHub,
    scanner: Scanner,
    concurrency: int,
) -> list[RepoOutcome]:
    sem = asyncio.Semaphore(concurrency)

    async def _guarded(repo: RepoSpec) -> RepoOutcome:
        async with sem:
            return await process_repository(
                repo,
                cloner=cloner,
                github=github,
                scanner=scanner,
            )

    results = await asyncio.gather(*[_guarded(s) for s in specs], return_exceptions=True)

    outcomes: list[RepoOutcome] = []
    for spec, result in zip(specs, results):
        if isinstance(result, BaseException):
            log.error("unexpected error for %s: %s", spec.url, result)
            outcomes.append(RepoOutcome(repo=spec, success=False, error=result))
        else:
            outcomes.append(result)
    return outcomes
