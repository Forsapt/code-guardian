import logging
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from code_guardian.models import RepoOutcome, Severity
from code_guardian.utils import report_name

log = logging.getLogger(__name__)

_SEVERITY_COLORS = {
    Severity.critical: colors.HexColor("#d33"),
    Severity.high: colors.HexColor("#e67e22"),
    Severity.medium: colors.HexColor("#f1c40f"),
    Severity.low: colors.HexColor("#95a5a6"),
    Severity.unknown: colors.HexColor("#bdc3c7"),
}


class PDFReportFile:
    def write(self, outcome: RepoOutcome, output_dir: Path) -> Path:
        name = report_name(outcome)
        path = output_dir / f"{name}.pdf"
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(str(path), pagesize=A4)
        story = []

        story.append(Paragraph(outcome.repo.url, styles["Title"]))
        story.append(Spacer(1, 12))

        pop = outcome.popularity
        if pop:
            story.append(Paragraph(f"Stars: {pop.stars}  |  Forks: {pop.forks}", styles["Normal"]))
            story.append(Spacer(1, 12))

        scan = outcome.scan_result
        counts = scan.severity_counts() if scan else {}
        stats_data = [["Severity", "Count"]] + [[s.value, str(counts.get(s, 0))] for s in Severity]
        stats_table = Table(stats_data)
        stats_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f5f5f5")],
                    ),
                ]
            )
        )
        story.append(stats_table)
        story.append(Spacer(1, 12))

        if scan and scan.vulnerabilities:
            vuln_data = [["ID", "Package", "Severity", "Title"]]
            for v in scan.vulnerabilities:
                vuln_data.append([v.id, v.pkg_name, v.severity.value, v.title[:60]])
            vuln_table = Table(vuln_data, colWidths=[90, 80, 60, 260])
            row_styles: list = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
            ]
            for i, v in enumerate(scan.vulnerabilities, start=1):
                cell_color = _SEVERITY_COLORS.get(v.severity)
                if cell_color:
                    row_styles.append(("BACKGROUND", (2, i), (2, i), cell_color))
            vuln_table.setStyle(TableStyle(row_styles))
            story.append(vuln_table)

        doc.build(story)
        log.info("report written %s", path)
        return path
