import logging

import httpx

from code_guardian.models import RepoPopularity

log = logging.getLogger(__name__)

_BASE = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self._headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    async def get_popularity(self, owner: str, repo: str) -> RepoPopularity:
        try:
            async with httpx.AsyncClient(headers=self._headers, timeout=10) as client:
                resp = await client.get(f"{_BASE}/repos/{owner}/{repo}")
                resp.raise_for_status()
                data = resp.json()
                return RepoPopularity(stars=data["stargazers_count"], forks=data["forks_count"])
        except Exception as exc:
            log.warning("popularity unavailable for %s/%s: %s", owner, repo, exc)
            return RepoPopularity.unknown()
