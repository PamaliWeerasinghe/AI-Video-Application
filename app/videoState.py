import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

# PARENT STATE (Holds only the final deliverables, No message history)
class VideoState(TypedDict):
    topic: str
    final_script: str
    qa_status: str
    video_file_paths: Annotated[list[str], operator.add]


# PRIVATE SUBGRAPH STATE
class DirectorState(TypedDict):
    script: str
    messages: Annotated[list[AnyMessage], add_messages]
    local_clips: Annotated[list[str], operator.add]


# Build the SubGraph (The Director's Private Loop)
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

# Compile into an executable subgraph
director_subgraph = director_builder.compile()

# Mapping Node (Bridging Parent and Child)
def call_director_subgraph(state: VideoState):
    """
    This wrapper node lives in the Parent Graph. It translates the Parent State
    into the Subgraph State, executes the subgraph, and translates the results back.
    """
    # Map Parent -> Child
    director_input = {
        "script": state["final_script"],
        "messages": [],
        "local_clips": [],
    }

    #Execute the Subgraph
    #The subgraph runs its own internal nodes, tool calls and retries privately.
    subgraph_result = director_subgraph.invoke(director_input)

    #Map Child -> Parent
    return {
        "video_file_paths": subgraph_result.get("local_clips", [])
    }

#Build the Parent Graph
parent_builder = StateGraph(VideoState)

#Add the wrapper node to the main workflow
parent_builder.add_node("director_agent", call_director_subgraph)

parent_builder.set_entry_point("director_agent")

parent_builder.add_edge("director_agent", END)

parent_graph = parent_builder.compile()

