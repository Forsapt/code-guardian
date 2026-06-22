from rich.console import Console
from rich.text import Text

from code_guardian.models import RepoOutcome, RepoPopularity, Severity

console = Console()

_SEV_STYLES = {
    Severity.critical: "bold red",
    Severity.high: "yellow",
    Severity.medium: "white",
    Severity.low: "dim",
}


def print_table(outcomes: list[RepoOutcome]) -> None:
    for outcome in outcomes:
        line1 = Text()
        line1.append("● ", style="bold")
        line1.append(outcome.repo.url)
        console.print(line1)

        if not outcome.success:
            console.print("  [red]error[/red]:", outcome.error)
            console.print()
            continue

        popularity = outcome.popularity or RepoPopularity.unknown()
        line2 = Text("  ")
        line2.append(f"★ {popularity.stars}", style="bold")
        line2.append(f"  ⑂ {popularity.forks}")
        console.print(line2)

        counts = outcome.scan_result.severity_counts() if outcome.scan_result else {}
        line3 = Text("  ")
        for sev in (Severity.critical, Severity.high, Severity.medium, Severity.low):
            label = sev.value[:4] if sev != Severity.medium else "MED"
            count = counts.get(sev, 0)
            line3.append(f"{label} {count}", style=_SEV_STYLES[sev] if count else "dim")
            line3.append("  ")
        line3.append("✓", style="green")
        console.print(line3)
        console.print()
