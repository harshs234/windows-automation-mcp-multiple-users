from typing import Any
from pydantic import BaseModel, Field


class CleanupResponse(BaseModel):
    status: str
    computerName: str
    spaceRecoveredGB: float
    cleanupPerformed: bool
    lockedFiles: int
    message: str
    dryRun: bool = False
    plannedCleanup: list[dict[str, Any]] | None = None
