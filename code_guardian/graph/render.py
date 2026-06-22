import logging
import subprocess
from pathlib import Path

from code_guardian.graph import GraphFormat
from code_guardian.models import ComponentGraph

log = logging.getLogger(__name__)


def render(graph: ComponentGraph, output_dir: Path, name: str, fmt: GraphFormat) -> Path:
    dot_src = graph.to_dot()

    if fmt == GraphFormat.dot:
        path = output_dir / f"{name}.dot"
        path.write_text(dot_src)
        log.info("graph written %s", path)
        return path

    dot_path = output_dir / f"{name}.dot"
    dot_path.write_text(dot_src)
    out_path = output_dir / f"{name}.{fmt.value}"
    try:
        subprocess.run(
            ["dot", f"-T{fmt.value}", str(dot_path), "-o", str(out_path)],
            check=True,
            capture_output=True,
        )
    finally:
        dot_path.unlink(missing_ok=True)
    log.info("graph written %s", out_path)
    return out_path
