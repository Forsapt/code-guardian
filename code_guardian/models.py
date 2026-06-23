import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Literal

_DOT_COLORS: dict[str, str] = {
    "CRITICAL": "#dd3333",
    "HIGH": "#e67e22",
    "MEDIUM": "#f1c40f",
    "LOW": "#95a5a6",
}


class Severity(StrEnum):
    unknown = "UNKNOWN"
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"


@dataclass(slots=True)
class Vulnerability:
    id: str
    pkg_name: str
    installed_version: str
    fixed_version: str
    severity: Severity
    title: str
    target: str = ""


@dataclass(slots=True)
class ScanResult:
    vulnerabilities: list[Vulnerability] = field(default_factory=list)

    def severity_counts(self) -> dict[Severity, int]:
        counts: dict[Severity, int] = dict.fromkeys(Severity, 0)
        for v in self.vulnerabilities:
            counts[v.severity] += 1
        return counts


_GITHUB_RE = re.compile(r"(?:https?://github\.com/|git@github\.com:)([^/]+)/([^/]+)")


@dataclass(slots=True)
class RepoSpec:
    url: str
    owner: str | None = None
    name: str | None = None

    @property
    def is_local(self) -> bool:
        return not self.url.startswith(("http://", "https://", "git@", "git://"))

    @classmethod
    def from_url(cls, raw: str) -> "RepoSpec":
        m = _GITHUB_RE.search(raw)
        if m:
            return cls(
                url=raw,
                owner=m.group(1),
                name=m.group(2).removesuffix(".git"),
            )
        return cls(url=raw)


@dataclass(slots=True)
class RepoPopularity:
    stars: int
    forks: int

    @classmethod
    def unknown(cls) -> "RepoPopularity":
        return cls(stars=0, forks=0)


@dataclass(slots=True)
class GraphNode:
    id: str
    label: str
    kind: Literal["target", "package", "vulnerability"]
    max_severity: Severity | None


@dataclass(slots=True)
class ComponentGraph:
    nodes: dict[str, GraphNode]
    edges: set[tuple[str, str]]

    def to_dot(self) -> str:
        lines = ["digraph {", "    graph [rankdir=LR]"]
        for node in self.nodes.values():
            eid = node.id.replace('"', '\\"')
            elabel = node.label.replace('"', '\\"')
            if node.kind == "target":
                lines.append(f'    "{eid}" [label="{elabel}" shape=folder color=navy]')
            elif node.kind == "package":
                color = _DOT_COLORS.get(node.max_severity or "") if node.max_severity else None
                if color:
                    lines.append(f'    "{eid}" [label="{elabel}" style=filled fillcolor="{color}"]')
                else:
                    lines.append(f'    "{eid}" [label="{elabel}"]')
            else:
                color = _DOT_COLORS.get(node.max_severity or "") if node.max_severity else "#eeeeee"
                lines.append(
                    f'    "{eid}" [label="{elabel}" shape=note fontsize=8'
                    f' style=filled fillcolor="{color}"]'
                )
        for src, dst in sorted(self.edges):
            esrc = src.replace('"', '\\"')
            edst = dst.replace('"', '\\"')
            lines.append(f'    "{esrc}" -> "{edst}"')
        lines.append("}")
        return "\n".join(lines)


@dataclass(slots=True)
class RepoOutcome:
    repo: RepoSpec
    success: bool
    popularity: RepoPopularity | None = None
    scan_result: ScanResult | None = None
    report_path: Path | None = None
    graph_path: Path | None = None
    error: BaseException | None = None
