from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.videoState import VideoState

STORYBOARD_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "storyboards"


class Scene(BaseModel):
    scene_number: int
    duration: int
    visual_prompt: str
    tts_audio: str
    transition: str


class Storyboard(BaseModel):
    scenes: list[Scene]
    cta_text: str


class DirectorState(TypedDict):
    script: str
    storyboard: Storyboard


def storyboard_node(state: DirectorState) -> dict[str, Storyboard]:
    llm = ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=0.7,
    )
    structured_llm = llm.with_structured_output(Storyboard)
    prompt = f"Parse the following video script into a structured storyboard:\n\n{state['script']}"
    storyboard = structured_llm.invoke([HumanMessage(content=prompt)])
    return {"storyboard": storyboard}


director_builder = StateGraph(DirectorState)
director_builder.add_node("storyboard", storyboard_node)
director_builder.set_entry_point("storyboard")
director_builder.add_edge("storyboard", END)
director_subgraph = director_builder.compile()


def _save_storyboard(topic: str, storyboard: Storyboard) -> Path:
    safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", topic).strip(" .")
    if not safe_title:
        raise ValueError("The topic cannot be used as a storyboard filename.")
    if re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$", safe_title, re.IGNORECASE):
        safe_title = f"_{safe_title}"

    STORYBOARD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    storyboard_path = STORYBOARD_OUTPUT_DIR / f"{safe_title}_{timestamp}.json"
    storyboard_path.write_text(
        storyboard.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return storyboard_path


def call_director_subgraph(state: VideoState) -> dict[str, Storyboard]:
    result = director_subgraph.invoke({"script": state["final_script"]})
    storyboard = result["storyboard"]
    storyboard_path = _save_storyboard(state["topic"], storyboard)
    print(f"Director: Saved storyboard to {storyboard_path}")
    return {"storyboard": storyboard}