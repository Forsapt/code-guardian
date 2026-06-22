from enum import StrEnum
from pathlib import Path
from typing import Protocol

from code_guardian.models import RepoOutcome


class ReportFormat(StrEnum):
    json = "json"
    pdf = "pdf"


class ReportWriter(Protocol):
    def write(self, outcome: RepoOutcome, output_dir: Path) -> Path: ...


def report_name(outcome: RepoOutcome) -> str:
    repo = outcome.repo
    if repo.owner and repo.name:
        return f"{repo.owner}-{repo.name}"
    return Path(repo.url).name


def get_reporter(fmt: ReportFormat) -> ReportWriter:
    from code_guardian.reporting.json_report import JSONReportFile
    from code_guardian.reporting.pdf_report import PDFReportFile

    reporters: dict[ReportFormat, ReportWriter] = {
        ReportFormat.json: JSONReportFile(),
        ReportFormat.pdf: PDFReportFile(),
    }
    if fmt not in reporters:
        raise ValueError(f"unsupported report format: {fmt!r}")
    return reporters[fmt]
