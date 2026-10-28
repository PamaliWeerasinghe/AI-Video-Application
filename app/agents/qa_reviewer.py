from tkinter import END

from app.videoState import VideoState

def qa(state: VideoState):
    #Reviews the clips in state["video_file_paths"]
    print(f"QA Reviewer: Reviewing clips: {state.get('video_file_paths')}")

    #Mocking that LLM found a policy violation
    
    #In a real app, the LLM decides "pass" or "fail" 
    status = "pass" 

    return {"status": status}


def qa_router(state: VideoState):
    """
    This function doesn't change the state. It just looks at the state 
    and returns a string telling LangGraph which node to go to next.
    """
    if state.get("qa_status") == "fail":
        print("Router: QA failed! Routing back to the Director...")
        return "director_agent"

    else:
        print("Router: QA passed! Routing to the Strategist...")
        return END