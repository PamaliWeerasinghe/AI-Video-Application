import os
from pathlib import Path
from typing import Any

from app.videoState import VideoState


VIDEOS_DIRECTORY = Path(__file__).resolve().parents[1] / "videos"
SUPPORTED_VIDEO_FORMATS = (".mp4", ".mov", ".avi")


def scan_video_directory(state: VideoState) -> dict[str, Any]:
    """Scan the application's videos directory and store the results in graph state."""
    directory_path = Path(state.get("video_directory", VIDEOS_DIRECTORY))
    if not os.path.exists(directory_path):
        scan_results = {
            "status": "error",
            "message": f"Directory not found: {directory_path}",
            "videos": []
        }
    else:
        found_videos = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(SUPPORTED_VIDEO_FORMATS):
                    found_videos.append(os.path.join(root, file))

        scan_results = {
            "status": "success",
            "videos": found_videos,
            "count": len(found_videos)
        }

    return {"scan_results": scan_results}