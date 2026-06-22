import asyncio
from pathlib import Path
from typing import Annotated

import typer

from code_guardian.adapters.github import GitHubClient
from code_guardian.models import RepoSpec
from code_guardian.pipeline import process_repository

app = typer.Typer(no_args_is_help=True)


@app.command()
def main(
    repos: Annotated[list[str], typer.Argument(help="Git URLs or local paths to scan")],
    output_dir: Annotated[Path, typer.Option("-o", "--output-dir")] = Path("reports"),
    concurrency: Annotated[int, typer.Option("-c", "--concurrency", min=1)] = 4,
) -> None:
    asyncio.run(_run(repos))


async def _run(urls: list[str]) -> None:
    github = GitHubClient()
    specs = [RepoSpec.from_url(url) for url in urls]
    outcomes = await asyncio.gather(*[process_repository(s, github=github) for s in specs])
    for outcome in outcomes:
        popularity = outcome.popularity
        typer.echo(f"{outcome.repo.url}: stars={popularity.stars} forks={popularity.forks}")


if __name__ == "__main__":
    app()
