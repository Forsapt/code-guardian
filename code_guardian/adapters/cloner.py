import asyncio
import logging
from pathlib import Path

from code_guardian.errors import CloneError

log = logging.getLogger(__name__)


class GitCloner:
    async def clone(self, url: str, dest: Path) -> None:
        log.info("cloning %s", url)
        proc = await asyncio.create_subprocess_exec(
            "git",
            "-c", "credential.helper=",
            "clone",
            "--depth=1",
            url,
            str(dest),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise CloneError(stderr.decode().strip())
        log.info("cloned %s", url)
