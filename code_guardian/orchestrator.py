import asyncio
import logging
from pathlib import Path

from code_guardian.graph import GraphFormat
from code_guardian.models import RepoOutcome, RepoSpec
from code_guardian.pipeline import Cloner, GitHub, Scanner, process_repository
from code_guardian.reporting import ReportWriter

log = logging.getLogger(__name__)


async def run(
    specs: list[RepoSpec],
    *,
    cloner: Cloner,
    github: GitHub,
    scanner: Scanner,
    reporter: ReportWriter,
    graph_format: GraphFormat,
    concurrency: int,
    output_dir: Path,
) -> list[RepoOutcome]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(concurrency)

    async def _guarded(repo: RepoSpec) -> RepoOutcome:
        async with sem:
            return await process_repository(
                repo,
                cloner=cloner,
                github=github,
                scanner=scanner,
                reporter=reporter,
                graph_format=graph_format,
                output_dir=output_dir,
            )

    results = await asyncio.gather(*[_guarded(s) for s in specs], return_exceptions=True)

    outcomes: list[RepoOutcome] = []
    for spec, result in zip(specs, results, strict=True):
        if isinstance(result, BaseException):
            log.error("unexpected error for %s: %s", spec.url, result)
            outcomes.append(RepoOutcome(repo=spec, success=False, error=result))
        else:
            outcomes.append(result)
    return outcomes
