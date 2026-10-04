# 1. Import state
from app.videoState import VideoState

# 2. Import agent nodes from their respective files
from app.agents.strategist import strategist
from app.agents.scriptwriter import scriptwriter
from app.agents.director import call_director_subgraph
from app.agents.qa_reviewer import qa, qa_router

# Initialize the graph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

parent_builder = StateGraph(VideoState)

# Add all your nodes
parent_builder.add_node("strategist", strategist)
parent_builder.add_node("scriptwriter", scriptwriter)
parent_builder.add_node("director", call_director_subgraph)
parent_builder.add_node("qa", qa)

# Define the sequential flow
parent_builder.set_entry_point("strategist")
parent_builder.add_edge("strategist", "scriptwriter")
parent_builder.add_edge("scriptwriter", "director")
parent_builder.add_edge("director", "qa")

# Define conditional feedback loop
parent_builder.add_conditional_edges(
    "qa_agent",
    qa_router
)

# Compile with memory checkpointing
memory = MemorySaver()
app = parent_builder.compile(checkpointer=memory, interrupt_before=["qa_agent"])