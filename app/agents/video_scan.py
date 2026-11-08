from pathlib import Path
from typing import Any


VIDEOS_DIRECTORY = Path(__file__).resolve().parents[2] / "videos"
INCOMING_VIDEO_DIRECTORY = VIDEOS_DIRECTORY / "incoming"
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


def scan_video_directory(state: dict[str, Any]) -> dict[str, Any]:
    video_directory = Path(state.get("video_directory", INCOMING_VIDEO_DIRECTORY))

    if not video_directory.is_dir():
        return {
            "new_videos": [],
            "has_new_videos": False,
            "scan_results": {
                "status": "error",
                "videos": [],
                "count": 0,
            },
        }

    videos = sorted(
        str(path)
        for path in video_directory.rglob("*")
        if path.is_file()
        and path.suffix.lower() in VIDEO_EXTENSIONS
        and "processed" not in path.relative_to(video_directory).parts
    )

    return {
        "new_videos": videos,
        "has_new_videos": bool(videos),
        "scan_results": {
            "status": "success",
            "videos": videos,
            "count": len(videos),
        },
    }
