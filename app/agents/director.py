from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

if TYPE_CHECKING:
    from app.videoState import VideoState


class DirectorState(TypedDict):
    script: str
    messages: Annotated[list[AnyMessage], add_messages]
    local_clips: Annotated[list[str], operator.add]


def storyboard_node(state: DirectorState):
    # LLM reads state["script"] and outputs tool calls to generate video
    # Should include the LLM logic
    return {"messages": [("ai", "Calling RunwayML for Scene 1...")]}


def render_tools_node(state: DirectorState):
    # Executes the video rendering MCP tools
    new_clips = ["/output/scene_1.mp4"]
    return {"local_clips": new_clips}


director_builder = StateGraph(DirectorState)

director_builder.add_node("storyboard", storyboard_node)
director_builder.add_node("render_tools", render_tools_node)

director_builder.set_entry_point("storyboard")
director_builder.add_edge("storyboard", "render_tools")
director_builder.add_edge("render_tools", END)

director_subgraph = director_builder.compile()


def call_director_subgraph(state: VideoState):
    """
    This wrapper node lives in the Parent Graph. It translates the Parent State
    into the Subgraph State, executes the subgraph, and translates the results back.
    """
    director_input = {
        "script": state["final_script"],
        "messages": [],
        "local_clips": [],
    }

    subgraph_result = director_subgraph.invoke(director_input)

    return {
        "video_file_paths": subgraph_result.get("local_clips", [])
    }
