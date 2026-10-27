import os
from typing import Dict, Any

def scan_video_directory(directory_path: str, supported_formats: tuple = ('.mp4', '.mov', '.avi')) -> Dict[str, Any]:
    """Scans a directory for video files and returns the findings."""
    
    if not os.path.exists(directory_path):
         # Return the error as data, do not raise an exception that breaks the graph
        return {
            "status": "error",
            "message": f"Directory not found: {directory_path}",
            "videos": []
        }
        
    found_videos = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(supported_formats):
                found_videos.append(os.path.join(root, file))
                
    return {
        "status": "success",
        "videos": found_videos,
        "count": len(found_videos)
    }