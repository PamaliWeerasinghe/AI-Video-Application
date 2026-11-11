import json
import re
from pathlib import Path
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.agent_output import agent_print as print
from app.agents.director import STORYBOARD_OUTPUT_DIR
from app.videoState import VideoState


CAPTIONS_DIRECTORY = Path(__file__).resolve().parents[2] / "captions"


def _load_storyboard_script(video_path: str) -> str:
    storyboard_path = STORYBOARD_OUTPUT_DIR / f"{Path(video_path).stem}.json"
    if not storyboard_path.is_file():
        raise FileNotFoundError(
            f"No storyboard found for video {video_path}: expected {storyboard_path}"
        )

    storyboard: Any = json.loads(storyboard_path.read_text(encoding="utf-8"))
    if not isinstance(storyboard, dict) or not isinstance(
        storyboard.get("scenes"), list
    ):
        raise ValueError(f"Invalid storyboard structure in {storyboard_path}.")

    narration = [
        scene["tts_audio"].strip()
        for scene in storyboard["scenes"]
        if isinstance(scene, dict)
        and isinstance(scene.get("tts_audio"), str)
        and scene["tts_audio"].strip()
    ]
    cta = storyboard.get("cta_text", "")
    if isinstance(cta, str) and cta.strip():
        narration.append(cta.strip())
    if not narration:
        raise ValueError(f"Storyboard contains no script text: {storyboard_path}")

    return "\n".join(narration)


def _save_caption(caption: str, video_path: str) -> Path:
    title = Path(video_path).stem
    safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title).strip(" .")
    if not safe_title:
        raise ValueError("The video title cannot be used as a caption filename.")
    if re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$", safe_title, re.IGNORECASE):
        safe_title = f"_{safe_title}"

    CAPTIONS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    caption_path = CAPTIONS_DIRECTORY / f"{safe_title}.txt"
    caption_path.write_text(caption, encoding="utf-8")
    return caption_path


def _generate_caption(topic: str, script: str) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Write an engaging, concise caption for a short-form social video. "
                "Use a natural tone, summarize the video's key idea, and include "
                "a few relevant hashtags. Do not claim details that are not in "
                "the supplied content. Return only the caption.",
            ),
            ("human", "Topic: {topic}\nVideo script: {final_script}"),
        ]
    )
    chain = prompt | ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=0.7,
    ) | StrOutputParser()
    caption = chain.invoke(
        {
            "topic": topic,
            "final_script": script,
        }
    ).strip()
    if not caption:
        raise ValueError(f"Caption generation returned an empty result for {topic}.")
    return caption


def create_caption(state: VideoState) -> dict[str, Any]:
    """Generate and save one storyboard-based caption for each scanned video."""
    print("Started creating a caption....")
    videos = state.get("new_videos", [])
    if not videos:
        raise ValueError("Cannot save the caption because no scanned video is available.")

    captions: dict[str, str] = {}
    for video_path in videos:
        topic = Path(video_path).stem
        script = _load_storyboard_script(video_path)
        caption = _generate_caption(topic, script)
        caption_path = _save_caption(caption, video_path)
        print(f"Saved caption to {caption_path}")
        captions[video_path] = caption

    return {"captions": captions, "caption": captions[videos[0]]}


create_captions = create_caption