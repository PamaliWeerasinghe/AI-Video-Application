# app/agents/publisher.py
import os
import shutil
from typing import Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

async def publish_videos_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    video_path = state.get("current_video")
    caption = state.get("caption", "")
    title = state.get("title", os.path.splitext(os.path.basename(video_path))[0])

    # Connect to the MCP Server
    server_params = StdioServerParameters(command="python", args=["mcp_social_publisher.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            tool_dict = {tool.name: tool for tool in tools}

            # 1. Publish to YouTube
            if "publish_to_youtube" in tool_dict:
                await tool_dict["publish_to_youtube"].ainvoke({
                    "video_path": video_path,
                    "title": title,
                    "description": caption
                })

            # 2. Publish to Facebook
            if "publish_to_facebook" in tool_dict:
                await tool_dict["publish_to_facebook"].ainvoke({
                    "video_path": video_path,
                    "caption": caption
                })

            # 3. Publish to TikTok
            if "publish_to_tiktok" in tool_dict:
                await tool_dict["publish_to_tiktok"].ainvoke({
                    "video_path": video_path,
                    "caption": caption
                })

    # Move video to processed directory so it isn't republished
    dest = os.path.join("videos/processed", os.path.basename(video_path))
    shutil.move(video_path, dest)
    print(f"Published and moved {video_path} to {dest}")

    return {"status": "published"}