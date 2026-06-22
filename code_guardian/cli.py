from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def main(
    repos: Annotated[list[str], typer.Argument(help="Git URLs or local paths to scan")],
    output_dir: Annotated[Path, typer.Option("-o", "--output-dir")] = Path("reports"),
    concurrency: Annotated[int, typer.Option("-c", "--concurrency", min=1)] = 4,
) -> None:
    typer.echo(f"Scanning {len(repos)} repo(s)...")
