import asyncio
from pathlib import Path

from code_guardian.errors import CloneError


class GitCloner:
    async def clone(self, url: str, dest: Path) -> None:
        proc = await asyncio.create_subprocess_exec(
            "git",
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
