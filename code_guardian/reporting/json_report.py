import json
import logging
from pathlib import Path

from code_guardian.models import RepoOutcome, Severity
from code_guardian.reporting import report_name

log = logging.getLogger(__name__)


def _serialize(outcome: RepoOutcome) -> dict:
    pop = outcome.popularity
    scan = outcome.scan_result
    counts = scan.severity_counts() if scan else {}
    return {
        "repository": outcome.repo.url,
        "popularity": {
            "stars": pop.stars if pop else 0,
            "forks": pop.forks if pop else 0,
        },
        "severity_stats": {s.value: counts.get(s, 0) for s in Severity},
        "vulnerabilities": [
            {
                "id": v.id,
                "pkg_name": v.pkg_name,
                "installed_version": v.installed_version,
                "fixed_version": v.fixed_version,
                "severity": v.severity.value,
                "title": v.title,
            }
            for v in (scan.vulnerabilities if scan else [])
        ],
    }


class JSONReportFile:
    def write(self, outcome: RepoOutcome, output_dir: Path) -> Path:
        name = report_name(outcome)
        path = output_dir / f"{name}.json"
        path.write_text(json.dumps(_serialize(outcome), indent=2))
        log.info("report written %s", path)
        return path
