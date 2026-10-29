import os
from typing import Dict, Any

VIDEO_DIR = "C:\\Agentic-AI\\AI-Video-Application\\app\\videos\\incoming"

def scan_video_directory(state: Dict[str, Any]) -> Dict[str, Any]:
    os.makedirs(VIDEO_DIR, exist_ok=True)
    valid_exts = (".mp4", ".mov", ".mkv", ".webm")
    
    videos = [
        os.path.join(VIDEO_DIR, f)
        for f in os.listdir(VIDEO_DIR)
        if f.lower().endswith(valid_exts)
    ]

    return {
        "new_videos": videos,
        "has_new_videos": len(videos) > 0
    }