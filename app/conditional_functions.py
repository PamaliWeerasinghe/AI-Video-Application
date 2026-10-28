from typing import Any

from app.agents.video_scan import VIDEOS_DIRECTORY, scan_video_directory


def video_scan_router_function(state: dict[str, Any]) -> bool:
    """Route to caption generation only when the scan found video files."""
    scan_results = state.get("scan_results")
    if scan_results is None:
        scan_results = scan_video_directory({"video_directory": str(VIDEOS_DIRECTORY)})[
            "scan_results"
        ]

    return scan_results.get("status") == "success" and bool(
        scan_results.get("videos")
    )