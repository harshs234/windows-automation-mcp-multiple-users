from app.models.response_models import CleanupResponse


def map_cleanup_response(ps_result: dict) -> CleanupResponse:
    recovered = float(ps_result.get("RecoveredGB", 0))
    errors = ps_result.get("Errors", []) or []

    return CleanupResponse(
        status="success",
        computerName=ps_result.get("ComputerName", ""),
        spaceRecoveredGB=recovered,
        cleanupPerformed=True,
        lockedFiles=len(errors),
        message=(
            "Disk cleanup completed successfully."
            if recovered > 0
            else "Cleanup completed. No additional space was recovered."
        ),
        dryRun=False,
    )


def map_preview_response(ps_result: dict) -> CleanupResponse:
    estimated = float(ps_result.get("EstimatedSpaceRecoveredGB", 0))
    return CleanupResponse(
        status="preview",
        computerName=ps_result.get("ComputerName", ""),
        spaceRecoveredGB=estimated,
        cleanupPerformed=False,
        lockedFiles=0,
        message=ps_result.get(
            "Message",
            "Preview only. No files were deleted.",
        ),
        dryRun=True,
        plannedCleanup=ps_result.get("PlannedCleanup"),
    )
