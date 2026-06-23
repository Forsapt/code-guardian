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
