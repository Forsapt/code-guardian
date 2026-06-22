import asyncio
import logging
import sys
from pathlib import Path
from typing import Annotated

import typer

from code_guardian.adapters.cloner import GitCloner
from code_guardian.adapters.github import GitHubClient
from code_guardian.adapters.trivy import TrivyScanner
from code_guardian.graph import GraphFormat
from code_guardian.models import RepoSpec
from code_guardian.orchestrator import run
from code_guardian.reporting import ReportFormat, get_reporter
from code_guardian.reporting.summary import print_table

app = typer.Typer(no_args_is_help=True)


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        stream=sys.stderr,
        level=level.upper(),
        format="%(levelname)s %(name)s: %(message)s",
    )


@app.command()
def main(
    repos: Annotated[list[str], typer.Argument(help="Git URLs or local paths to scan")],
    output_dir: Annotated[Path, typer.Option("-o", "--output-dir")] = Path("reports"),
    concurrency: Annotated[int, typer.Option("-c", "--concurrency", min=1)] = 4,
    report_format: Annotated[ReportFormat, typer.Option("--report-format")] = ReportFormat.json,
    graph_format: Annotated[GraphFormat, typer.Option("--graph-format")] = GraphFormat.svg,
    log_level: Annotated[str, typer.Option("--log-level")] = "info",
) -> None:
    _setup_logging(log_level)
    asyncio.run(
        _run(
            repos,
            concurrency=concurrency,
            output_dir=output_dir,
            report_format=report_format,
            graph_format=graph_format,
        )
    )


async def _run(
    urls: list[str],
    *,
    concurrency: int,
    output_dir: Path,
    report_format: ReportFormat,
    graph_format: GraphFormat,
) -> None:
    outcomes = await run(
        [RepoSpec.from_url(url) for url in urls],
        cloner=GitCloner(),
        github=GitHubClient(),
        scanner=TrivyScanner(),
        reporter=get_reporter(report_format),
        graph_format=graph_format,
        concurrency=concurrency,
        output_dir=output_dir,
    )
    print_table(outcomes)


if __name__ == "__main__":
    app()
