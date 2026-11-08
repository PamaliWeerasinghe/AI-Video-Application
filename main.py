import asyncio

try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()  # Load environment variables from .env file
from app.graph import app

async def run():
    #Configuration required for checkpoint memory (thread tracking)
    config = {
        "configurable":{"thread_id":"video_session_1"}
    }

    initial_input = {
        "final_script":"",
        "qa_status":"",
        "video_file_paths":[]
    }

# Run until it hits the interrupt before qa_agent
    async for event in app.astream(initial_input, config=config):
        print(f"Event: {event}")

if __name__ == "__main__":
    asyncio.run(run())