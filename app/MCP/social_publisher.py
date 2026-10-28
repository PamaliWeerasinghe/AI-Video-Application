# mcp_social_publisher.py
import os
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("Social-Media-Publisher")

PAGE_ID = os.getenv("FB_PAGE_ID", "61596111743315")
ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

@mcp.tool()
def publish_to_facebook(video_path: str, caption: str) -> str:
    """Uploads and publishes a video/Reel to the Facebook Page."""
    if not os.path.exists(video_path):
        return f"Error: File {video_path} not found."

    file_size = os.path.getsize(video_path)
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"

    with httpx.Client(timeout=180.0) as client:
        # Step 1: Start upload session
        start_res = client.post(url, data={
            "upload_phase": "start",
            "access_token": ACCESS_TOKEN
        })
        if start_res.status_code != 200:
            return f"Session error: {start_res.text}"

        session_data = start_res.json()
        video_id = session_data["video_id"]
        upload_url = session_data["upload_url"]

        # Step 2: Upload video binary
        headers = {
            "Authorization": f"OAuth {ACCESS_TOKEN}",
            "offset": "0",
            "file_size": str(file_size)
        }
        with open(video_path, "rb") as f:
            upload_res = client.post(upload_url, headers=headers, content=f.read())

        if upload_res.status_code != 200:
            return f"Upload error: {upload_res.text}"

        # Step 3: Finish and publish post
        finish_res = client.post(url, data={
            "upload_phase": "finish",
            "access_token": ACCESS_TOKEN,
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": caption
        })
        if finish_res.status_code != 200:
            return f"Publish error: {finish_res.text}"

    return f"Successfully published to Facebook! Video ID: {video_id}"

if __name__ == "__main__":
    mcp.run()