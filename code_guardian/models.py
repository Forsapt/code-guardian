import re
from dataclasses import dataclass

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
            return cls(url=raw, owner=m.group(1), name=m.group(2))
        return cls(url=raw)


@dataclass(slots=True)
class RepoPopularity:
    stars: int
    forks: int

    @classmethod
    def unknown(cls) -> 'RepoPopularity':
        return cls(stars=0, forks=0)


@dataclass(slots=True)
class RepoOutcome:
    repo: RepoSpec
    popularity: RepoPopularity
