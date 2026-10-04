from app.models.video_state import VideoState

def scriptwriter(state: VideoState):
    #Read the topic, writes the script
    topic = state.get("topic", "No topic found")
    print(f"Scriptwriter: Writing script for topic: {topic}")

    #Mocking the LLM output
    script = "Hook: Want an EV but broke? Body: Here are 3 cars under 30k..."

    return {"final_script": script}
