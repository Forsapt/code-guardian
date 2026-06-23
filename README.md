# code-guardian

CLI wrapper for Trivy that scans Git repositories and reports vulnerabilities.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- [Trivy](https://github.com/aquasecurity/trivy)
- [Graphviz](https://graphviz.org/) (`dot` in PATH)

## Local

```bash
uv sync
uv run python -m code_guardian.cli https://github.com/org/repo
```

Scan multiple repos with custom options:

```bash
uv run python -m code_guardian.cli \
  https://github.com/expressjs/express \
  https://github.com/axios/axios \
  --output-dir ./out \
  --concurrency 8 \
  --report-format pdf \
  --graph-format png \
  --log-level debug
```

## Docker

Build:

```bash
docker build -t code-guardian .
```

Run (reports are written inside the container — mount a volume to get them):

```bash
docker run --rm \
  -v "$(pwd)/reports:/app/reports" \
  code-guardian \
  https://github.com/org/repo
```

With options:

```bash
docker run --rm \
  -v "$(pwd)/reports:/app/reports" \
  code-guardian \
  https://github.com/org/repo \
  --output-dir /app/reports \
  --report-format pdf \
  --concurrency 2
```

## CLI reference

```
Usage: python -m code_guardian.cli [OPTIONS] REPOS...
```

| Argument / Flag | Default | Description |
|---|---|---|
| `REPOS...` | — | Git URLs or local paths to scan (one or more) |
| `-o`, `--output-dir PATH` | `reports` | Directory where reports and graphs are saved |
| `-c`, `--concurrency INT` | `4` | Maximum number of repos scanned in parallel (≥ 1) |
| `--report-format [json\|pdf]` | `json` | Report file format |
| `--graph-format [svg\|png\|dot]` | `svg` | Dependency graph output format |
| `--log-level TEXT` | `info` | Logging verbosity (`debug`, `info`, `warning`, `error`) |

Each scanned repo produces two files in `--output-dir`:

- `<owner>-<repo>.<report-format>` — full vulnerability report
- `<owner>-<repo>.<graph-format>` — dependency graph (target → package → CVE)

## Design decisions

### Concurrency model

Scanning is I/O-bound: cloning, spawning Trivy as a subprocess, GitHub API. `asyncio.gather` with a semaphore covers all three without threads or a process pool. The semaphore (`--concurrency`, default 4) limits how many Trivy processes run at once, since Trivy itself is CPU-heavy.

### Trivy integration

Trivy is invoked with `--output <tmpfile>` rather than reading stdout. The JSON is loaded after the process exits. For very large monorepos, streaming parse would be worth it, but for typical repos this is fine.

### Repository popularity

Only GitHub is supported via the public API (stars/forks). For GitLab, Bitbucket etc., a yt-dlp-style extractor pattern would work well: one extractor class per host, picked by URL prefix.

### Architecture: Protocol-based adapters

`Cloner`, `GitHub`, `Scanner`, and `ReportWriter` are structural `Protocol`s. The pipeline (`pipeline.py`) depends only on the interfaces; concrete adapters live in `adapters/`. Tests use simple fakes instead of hitting real subprocesses or APIs.

### Error resilience

Each repo is processed independently. Clone/scan failures are caught at the pipeline boundary and stored as a failed `RepoOutcome`; the run continues. Anything uncaught bubbles to the orchestrator via `asyncio.gather(return_exceptions=True)`. The final summary always includes every repo that was requested.

### Cloning and authentication

Clone runs with `credential.helper=` to avoid interactive prompts in Docker. Private repos aren't supported yet. To add it: pass credentials via env vars or a flag, either SSH key or username/password.

### Report format

JSON by default, PDF as an option. JSON is easier to pipe into other tools; PDF is for sharing with people.

### Dependency graph

SVG by default since it scales and embeds well. DOT is available if you want to process the graph further.

### Docker packaging

Multi-stage build: `uv` installs the virtualenv in one stage, the Trivy binary comes from `aquasec/trivy`, and the final image is slim Python 3.12 with `git` and `graphviz`.