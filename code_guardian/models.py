import re
from dataclasses import dataclass, field
from enum import StrEnum


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


@dataclass(slots=True)
class ScanResult:
    vulnerabilities: list[Vulnerability] = field(default_factory=list)

    def severity_counts(self) -> dict[Severity, int]:
        counts: dict[Severity, int] = dict.fromkeys(Severity, 0)
        for v in self.vulnerabilities:
            counts[v.severity] += 1
        return counts


_GITHUB_RE = re.compile(r"(?:https?://github\.com/|git@github\.com:)([^/]+)/([^/\.]+)")


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
                name=m.group(2),
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
class RepoOutcome:
    repo: RepoSpec
    success: bool
    popularity: RepoPopularity | None = None
    scan_result: ScanResult | None = None
    error: BaseException | None = None
