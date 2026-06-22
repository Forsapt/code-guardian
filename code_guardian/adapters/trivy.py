import asyncio
import json
import logging
import tempfile
from pathlib import Path

from code_guardian.errors import ScanError
from code_guardian.models import ScanResult, Severity, Vulnerability

log = logging.getLogger(__name__)


class TrivyScanner:
    async def scan(self, path: Path) -> ScanResult:
        log.info("scanning %s", path)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.json"
            proc = await asyncio.create_subprocess_exec(
                "trivy", "fs",
                "--format", "json",
                "--output", str(output_file),
                "--scanners", "vuln",
                "--quiet",
                str(path),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                msg = stderr.decode().strip()
                log.error("scan failed %s: %s", path, msg)
                raise ScanError(msg)
            result = _parse(output_file)
            log.info("scanned %s: %d vulnerabilities", path, len(result.vulnerabilities))
            return result

    async def available(self) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                "trivy", "--version",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()
            return proc.returncode == 0
        except FileNotFoundError:
            return False


def _parse(path: Path) -> ScanResult:
    data = json.loads(path.read_text())
    vulns: list[Vulnerability] = []
    for result in data.get("Results") or []:
        for v in result.get("Vulnerabilities") or []:
            vulns.append(
                Vulnerability(
                    id=v.get("VulnerabilityID", ""),
                    pkg_name=v.get("PkgName", ""),
                    installed_version=v.get("InstalledVersion", ""),
                    fixed_version=v.get("FixedVersion", ""),
                    severity=Severity(v.get("Severity", "UNKNOWN")),
                    title=v.get("Title", ""),
                )
            )
    return ScanResult(vulnerabilities=vulns)
