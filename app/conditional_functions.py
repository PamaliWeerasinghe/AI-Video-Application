from typing import Any, Dict

# Assuming your state is passed as a dict or a TypedDict containing 'scan_results'
def video_scan_router_function(state: Dict[str, Any]) -> str:
    print("Scanning Video Directory...")
    """
    Determines the next graph node based on the directory scan results.
    """
    scan_results = state.get("scan_results", {})
    status = scan_results.get("status")
    videos = scan_results.get("videos", [])
    
    # Route 1: The path was invalid or an OS error occurred
    if status == "error":
        return "handle_error_node"
        
    # Route 2: The scan worked, but the folder was empty
    if status == "success" and len(videos) == 0:
        return "end" # Or return to a node asking the user for a different path
        
    # Route 3: Videos found, proceed to processing
    return "process_videos_node"