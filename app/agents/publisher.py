import os
import shutil
from typing import Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

async def publish_videos_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    new_videos = state.get("new_videos", [])
    caption = state.get("caption", "Automated Daily Video Update")

    if not new_videos:
        print("No videos to publish.")
        return {"status": "skipped"}

    # Connect to the MCP Server
    server_params = StdioServerParameters(command="python", args=["mcp_social_publisher.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            tool_dict = {tool.name: tool for tool in tools}

            for video_path in new_videos:
                print(f"Publishing {video_path} to Facebook...")
                if "publish_to_facebook" in tool_dict:
                    result = await tool_dict["publish_to_facebook"].ainvoke({
                        "video_path": video_path,
                        "caption": caption
                    })
                    print(result)

                # Move video to processed so it isn't uploaded again
                dest = os.path.join("videos/processed", os.path.basename(video_path))
                shutil.move(video_path, dest)
                print(f"Moved {video_path} to {dest}")

    return {"status": "completed"}