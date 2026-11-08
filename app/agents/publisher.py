# app/agents/publisher.py
import shutil
import sys
from pathlib import Path
from typing import Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

from app.agents.director import STORYBOARD_OUTPUT_DIR
from app.agents.video_scan import VIDEOS_DIRECTORY

PUBLISHED_STORYBOARD_DIRECTORY = STORYBOARD_OUTPUT_DIR / "published"


def _move_storyboard_for_video(video_path: str) -> Path | None:
    storyboard_path = STORYBOARD_OUTPUT_DIR / f"{Path(video_path).stem}.json"
    if not storyboard_path.is_file():
        print(f"No matching storyboard found for {video_path}.")
        return None

    PUBLISHED_STORYBOARD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = PUBLISHED_STORYBOARD_DIRECTORY / storyboard_path.name
    shutil.move(str(storyboard_path), str(destination))
    print(f"Moved {storyboard_path} -> {destination}")
    return destination


async def publish_videos_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    new_videos = state.get("new_videos", [])
    caption = state.get("caption", "AI Generated Video Update")

    if not new_videos:
        print("No videos found to publish.")
        return {"publish_status": "skipped"}

    processed_directory = VIDEOS_DIRECTORY / "processed"
    processed_directory.mkdir(parents=True, exist_ok=True)
    server_path = Path(__file__).resolve().parents[1] / "MCP" / "social_publisher.py"
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            tool_dict = {tool.name: tool for tool in tools}

            for video_path in new_videos:
                print(f"Publishing {video_path}...")
                if "publish_to_facebook" not in tool_dict:
                    raise RuntimeError("Facebook publishing tool is unavailable.")

                result = await tool_dict["publish_to_facebook"].ainvoke({
                    "video_path": video_path,
                    "caption": caption
                })
                print(result)
                if not isinstance(result, str) or not result.startswith(
                    "Successfully published to Facebook!"
                ):
                    raise RuntimeError(
                        f"Failed to publish {video_path}: {result}"
                    )

                # Move out of videos to avoid re-uploading
                dest = processed_directory / Path(video_path).name
                shutil.move(video_path, str(dest))
                print(f"Moved {video_path} -> {dest}")
                _move_storyboard_for_video(video_path)

    return {"publish_status": "completed"}