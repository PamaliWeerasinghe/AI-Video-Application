import operator
from typing import Annotated, Any, TypedDict

from typing_extensions import NotRequired

from langgraph.graph import END, StateGraph

from app.agents.director import Storyboard, call_director_subgraph

# PARENT STATE (Holds only the final deliverables, No message history)
class VideoState(TypedDict):
    topic: str
    short_description: str
    final_script: str
    caption: str
    qa_status: str
    video_file_paths: Annotated[list[str], operator.add]
    storyboard: Storyboard
    scan_results: NotRequired[dict[str, Any]]
    video_directory: NotRequired[str]


#Build the Parent Graph
parent_builder = StateGraph(VideoState)

#Add the wrapper node to the main workflow
parent_builder.add_node("director_agent", call_director_subgraph)

parent_builder.set_entry_point("director_agent")

parent_builder.add_edge("director_agent", END)

parent_graph = parent_builder.compile()
