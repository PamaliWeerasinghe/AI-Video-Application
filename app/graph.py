# 1. Import state
from app.videoState import VideoState
from app.conditional_functions import video_scan_router_function

# 2. Import agent nodes from their respective files
from app.agents.strategist import strategist
from app.agents.scriptwriter import scriptwriter
from app.agents.director import call_director_subgraph
from app.agents.qa_reviewer import qa, qa_router
from app.agents.video_scan import scan_video_directory
from app.agents.captions import create_caption
from app.agents.publisher import publish_videos_agent

# Initialize the graph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

parent_builder = StateGraph(VideoState)

# Add all your nodes
parent_builder.add_node("strategist", strategist)
parent_builder.add_node("scriptwriter", scriptwriter)
parent_builder.add_node("director", call_director_subgraph)
parent_builder.add_node("qa", qa)
parent_builder.add_node("video_scan",scan_video_directory)
parent_builder.add_node("caption", create_caption)
parent_builder.add_node("publisher",publish_videos_agent)

# Define the sequential flow
parent_builder.set_entry_point("strategist")
parent_builder.add_edge("strategist", "scriptwriter")
parent_builder.add_edge("scriptwriter", "director")
parent_builder.add_edge("director", "qa")
parent_builder.add_edge("qa", "video_scan")

# Conditional loop to check whether videos directory has got videos
parent_builder.add_conditional_edges(
    "video_scan",
    video_scan_router_function,
    {
        "has_videos": "caption",
        "no_videos": END,
    },
)

parent_builder.add_edge("caption","publisher")
parent_builder.add_edge("publisher", END)

# Define conditional feedback loop
# parent_builder.add_conditional_edges(
#     "qa",
#     qa_router
# )

# Compile with memory checkpointing
memory = MemorySaver()
# app = parent_builder.compile(checkpointer=memory, interrupt_before=["qa"])
app = parent_builder.compile(checkpointer=memory)