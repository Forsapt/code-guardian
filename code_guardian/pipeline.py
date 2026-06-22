import logging
import shutil
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Protocol

from code_guardian.errors import CloneError, ScanError
from code_guardian.graph import GraphFormat
from code_guardian.graph.builder import build_graph
from code_guardian.graph.render import render
from code_guardian.models import RepoOutcome, RepoPopularity, RepoSpec, ScanResult
from code_guardian.reporting import ReportWriter
from code_guardian.utils import report_name

log = logging.getLogger(__name__)


class Cloner(Protocol):
    async def clone(self, url: str, dest: Path) -> None: ...


class GitHub(Protocol):
    async def get_popularity(self, owner: str, repo: str) -> RepoPopularity: ...


class Scanner(Protocol):
    async def scan(self, path: Path) -> ScanResult: ...


@asynccontextmanager
async def workspace() -> AsyncGenerator[Path, None]:
    path = Path(tempfile.mkdtemp(prefix="cg-"))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


async def process_repository(
    repo: RepoSpec,
    *,
    cloner: Cloner,
    github: GitHub,
    scanner: Scanner,
    reporter: ReportWriter,
    graph_format: GraphFormat,
    output_dir: Path,
) -> RepoOutcome:
    log.info("start %s", repo.url)

    if repo.is_local:
        outcome = await _process(
            repo,
            path=Path(repo.url),
            github=github,
            scanner=scanner,
            reporter=reporter,
            graph_format=graph_format,
            output_dir=output_dir,
        )
    else:
        async with workspace() as ws:
            try:
                await cloner.clone(repo.url, ws)
            except CloneError as exc:
                log.error("clone failed %s: %s", repo.url, exc)
                return RepoOutcome(repo=repo, success=False, error=exc)
            outcome = await _process(
                repo,
                path=ws,
                github=github,
                scanner=scanner,
                reporter=reporter,
                graph_format=graph_format,
                output_dir=output_dir,
            )

    if outcome.success:
        log.info("done %s", repo.url)
    else:
        log.error("failed %s: %s", repo.url, outcome.error)
    return outcome


async def _process(
    repo: RepoSpec,
    *,
    path: Path,
    github: GitHub,
    scanner: Scanner,
    reporter: ReportWriter,
    graph_format: GraphFormat,
    output_dir: Path,
) -> RepoOutcome:
    if repo.owner and repo.name:
        popularity = await github.get_popularity(repo.owner, repo.name)
    else:
        popularity = RepoPopularity.unknown()

    try:
        scan_result = await scanner.scan(path)
    except ScanError as exc:
        return RepoOutcome(repo=repo, success=False, error=exc)

    outcome = RepoOutcome(
        repo=repo,
        success=True,
        popularity=popularity,
        scan_result=scan_result,
    )
    outcome.report_path = reporter.write(outcome, output_dir)
    graph = build_graph(scan_result)
    outcome.graph_path = render(graph, output_dir, report_name(outcome), graph_format)
    return outcome
