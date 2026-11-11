from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.videoState import VideoState

STORYBOARD_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "storyboards"


class Scene(BaseModel):
    scene_number: int
    duration: float
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
    structured_llm = llm.with_structured_output(
        Storyboard,
        method="json_mode",
    )

    prompt = f"""You are an AI video director. Parse the following 10-second script into a structured 3-scene storyboard for video generation and synchronized captions.

TIMING & SYNC RULES:
- Total video duration is strictly 10.0 seconds.
- Scene 1: 0.0s - 3.0s (Hook - 3.0s duration)
- Scene 2: 3.0s - 7.0s (Body - 4.0s duration)
- Scene 3: 7.0s - 10.0s (Conclusion - 3.0s duration)

VISUAL & REALISM CONSTRAINTS:
- Realistic & Cinematic: Visual descriptions must describe 4K realistic, grounded real-world B-roll (cinematic camera angles, natural lighting, authentic documentary style).
- STRICTLY FORBIDDEN: No cartoon stickers, jumping animated GIFs, popup emojis, or subscribe buttons.

OUTPUT FORMAT:
Return strictly a valid JSON object (no markdown, no extra conversational text) with this exact structure:
{{
  "scenes": [
    {{
      "scene_number": 1,
      "duration": 3.0,
      "visual_prompt": "Photorealistic 4K cinematic scene description (no cartoons or GIFs)",
      "tts_audio": "Exact hook spoken words",
      "transition": "Cut"
    }},
    {{
      "scene_number": 2,
      "duration": 4.0,
      "visual_prompt": "Photorealistic 4K cinematic scene description (no cartoons or GIFs)",
      "tts_audio": "Exact body spoken words",
      "transition": "Cut"
    }},
    {{
      "scene_number": 3,
      "duration": 3.0,
      "visual_prompt": "Photorealistic 4K cinematic scene description (no cartoons or GIFs)",
      "tts_audio": "Exact conclusion spoken words",
      "transition": "Cut"
    }}
  ],
  "cta_text": "Optional call to action, or an empty string"
}}

Script to parse:
{state['script']}"""

    storyboard = structured_llm.invoke(prompt)
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
    # print(f"Director: Saved storyboard to {storyboard_path}")
    return {"storyboard": storyboard}