from code_guardian.models import RepoPopularity, RepoSpec


def test_from_url_github_https():
    spec = RepoSpec.from_url("https://github.com/OWASP/NodeGoat")
    assert spec.owner == "OWASP"
    assert spec.name == "NodeGoat"
    assert not spec.is_local


def test_from_url_github_ssh():
    spec = RepoSpec.from_url("git@github.com:OWASP/NodeGoat.git")
    assert spec.owner == "OWASP"
    assert spec.name == "NodeGoat"
    assert not spec.is_local


def test_from_url_local():
    spec = RepoSpec.from_url("/home/user/project")
    assert spec.owner is None
    assert spec.name is None
    assert spec.is_local


def test_from_url_name_with_dot():
    spec = RepoSpec.from_url("https://github.com/vercel/next.js")
    assert spec.owner == "vercel"
    assert spec.name == "next.js"


def test_from_url_strips_git_suffix():
    spec = RepoSpec.from_url("https://github.com/OWASP/NodeGoat.git")
    assert spec.name == "NodeGoat"


def test_popularity_unknown():
    pop = RepoPopularity.unknown()
    assert pop.stars == 0
    assert pop.forks == 0
