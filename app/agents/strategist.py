from app.models.video_state import VideoState


def strategist(state: VideoState):
    #Calls an LLM with search tools
    print("Strategist: Finding trending Facebook topics...")
    return {"topic": "Top 3 Budget EVs for 2026"}
