from app.conditional_functions import video_scan_router_function


def test_video_scan_router_selects_publish_path_when_incoming_videos_exist() -> None:
    assert video_scan_router_function({"new_videos": ["incoming/clip.mp4"]}) == (
        "has_videos"
    )


def test_video_scan_router_selects_storyboard_path_when_no_videos_exist() -> None:
    assert video_scan_router_function({"new_videos": []}) == "no_videos"
