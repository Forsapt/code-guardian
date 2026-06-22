from code_guardian.adapters.github import GitHubClient
from code_guardian.models import RepoOutcome, RepoPopularity, RepoSpec


async def process_repository(repo: RepoSpec, *, github: GitHubClient) -> RepoOutcome:
    if repo.owner and repo.name:
        popularity = await github.get_popularity(repo.owner, repo.name)
    else:
        popularity = RepoPopularity.unknown()
    return RepoOutcome(repo=repo, popularity=popularity)
