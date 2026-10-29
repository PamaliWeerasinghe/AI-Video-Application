# app/conditional_functions.py
from typing import Dict, Any

def video_scan_router_function(state: Dict[str, Any]) -> str:
    print("Scanning Video Directory...")
    
    new_videos = state.get("new_videos", [])
    if new_videos:
        print(f"Found {len(new_videos)} video(s) ready for captioning and upload.")
        return "has_videos"

    print("No new videos found in videos/incoming/.")
    return "no_videos"