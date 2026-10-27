from mcp.server.fastmcp import FastMCP
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Social-Media-Publisher")

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

@mcp.tool()
def publish_to_facebook(video_path: str, caption: str) -> str:
    """Uploads and publishes a video/Reel to your Facebook Page."""
    if not os.path.exists(video_path):
        return f"Error: Video file not found at {video_path}"

    file_size = os.path.getsize(video_path)
    init_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/video_reels"

    with httpx.Client(timeout=120.0) as client:
        # Phase 1: Start upload session
        init_res = client.post(init_url, data={
            "upload_phase": "start",
            "access_token": FB_PAGE_ACCESS_TOKEN
        })
        if init_res.status_code != 200:
            return f"Failed to initialize upload: {init_res.text}"

        data = init_res.json()
        video_id = data["video_id"]
        upload_url = data["upload_url"]

        # Phase 2: Stream video bytes
        headers = {
            "Authorization": f"OAuth {FB_PAGE_ACCESS_TOKEN}",
            "offset": "0",
            "file_size": str(file_size)
        }
        with open(video_path, "rb") as f:
            upload_res = client.post(upload_url, headers=headers, content=f.read())

        if upload_res.status_code != 200:
            return f"Failed to upload video content: {upload_res.text}"

        # Phase 3: Publish with caption
        finish_res = client.post(init_url, data={
            "upload_phase": "finish",
            "access_token": FB_PAGE_ACCESS_TOKEN,
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": caption
        })
        if finish_res.status_code != 200:
            return f"Failed to publish post: {finish_res.text}"

    return f"Successfully published to Facebook! Video ID: {video_id}"

if __name__ == "__main__":
    mcp.run()