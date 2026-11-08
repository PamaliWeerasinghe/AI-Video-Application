# web_dashboard.py
import json
import asyncio
import threading
import traceback
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse
from app.agent_output import capture_agent_output
from app.graph import app as graph_app

app = FastAPI(title="AI Video Agent Monitor")

AGENT_SEQUENCE = [
    "initial_video_scan",
    "strategist",
    "scriptwriter",
    "director",
    "qa",
    "video_scan",
    "caption",
    "publisher",
]
pipeline_stream_lock = asyncio.Lock()


class QueueOutput:
    def __init__(self, loop, output_queue):
        self.loop = loop
        self.output_queue = output_queue
        self.loop_thread_id = threading.get_ident()

    def write(self, text):
        if not text:
            return 0
        message = ("output", text)
        if threading.get_ident() == self.loop_thread_id:
            self.output_queue.put_nowait(message)
        else:
            self.loop.call_soon_threadsafe(self.output_queue.put_nowait, message)
        return len(text)

    def flush(self):
        pass

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/stream-pipeline")
async def stream_pipeline():
    async def event_generator():
        initial_input = {}
        config = {"configurable": {"thread_id": "web_run"}}

        yield {
            "event": "message",
            "data": json.dumps({"type": "init", "nodes": AGENT_SEQUENCE})
        }

        current_node = None
        async with pipeline_stream_lock:
            output_queue = asyncio.Queue()
            output_sink = QueueOutput(asyncio.get_running_loop(), output_queue)

            async def run_graph():
                try:
                    with capture_agent_output(output_sink.write):
                        async for event in graph_app.astream_events(
                            initial_input, config=config, version="v2"
                        ):
                            await output_queue.put(("graph_event", event))
                    await output_queue.put(("completed", None))
                except Exception as error:
                    await output_queue.put(
                        ("error", (error, traceback.format_exc()))
                    )

            graph_task = asyncio.create_task(run_graph())
            try:
                while True:
                    message_type, payload = await output_queue.get()

                    if message_type == "output":
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "type": "agent_output",
                                "agent": current_node or "pipeline",
                                "content": payload,
                            }),
                        }
                        continue

                    if message_type == "completed":
                        yield {
                            "event": "message",
                            "data": json.dumps({"type": "completed"}),
                        }
                        break

                    if message_type == "error":
                        error, stack = payload
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "type": "error",
                                "failed_node": current_node or "Unknown",
                                "error_message": str(error),
                                "stack_trace": stack,
                            }),
                        }
                        break

                    event_type = payload.get("event")
                    metadata = payload.get("metadata", {})
                    node = metadata.get("langgraph_node")
                    if node not in AGENT_SEQUENCE:
                        continue

                    if event_type == "on_chain_start" and node != current_node:
                        current_node = node
                        curr_idx = AGENT_SEQUENCE.index(node)
                        next_node = (
                            AGENT_SEQUENCE[curr_idx + 1]
                            if curr_idx + 1 < len(AGENT_SEQUENCE)
                            else "END"
                        )
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "type": "node_start",
                                "current_node": node,
                                "next_node": next_node,
                            }),
                        }
                    elif event_type == "on_chain_end" and node == current_node:
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "type": "node_success",
                                "node": node,
                                "output": str(
                                    payload.get("data", {}).get("output", "")
                                )[:200],
                            }),
                        }
            finally:
                if not graph_task.done():
                    graph_task.cancel()
                await asyncio.gather(graph_task, return_exceptions=True)

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_dashboard:app", host="0.0.0.0", port=8000, reload=True)