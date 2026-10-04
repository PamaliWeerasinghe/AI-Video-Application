try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()  # Load environment variables from .env file
from app.graph import app

def run():
    #Configuration required for checkpoint memory (thread tracking)
    config = {
        "configurable":{"thread_id":"video_session_1"}
    }

    initial_input = {
        "topic" : "Trending AI tools",
        "final_script":"",
        "qa_status":"",
        "video_file_paths":[]
    }

# Run until it hits the interrupt before qa_agent
    for event in app.stream(initial_input, config=config):
        print(f"Event: {event}")

if __name__ == "__main__":
    run()