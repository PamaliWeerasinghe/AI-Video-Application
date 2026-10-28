import re
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.videoState import VideoState


CAPTIONS_DIRECTORY = Path(__file__).resolve().parents[2] / "captions"


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


def create_caption(state: VideoState) -> dict[str, str]:
    """Generate a caption and save it under the scanned video's title."""
    print("Started creating a caption....")
    print(state.get("final_script", ""))
    videos = state.get("scan_results", {}).get("videos", [])
    if not videos:
        raise ValueError("Cannot save the caption because no scanned video is available.")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Write an engaging, concise caption for a short-form social video. "
                "Use a natural tone, summarize the video's key idea, and include "
                "a few relevant hashtags. Do not claim details that are not in "
                "the supplied content. Return only the caption.",
            ),
            (
                "human",
                "Topic: {topic}\n"
                "Description: {short_description}\n"
                "Video script: {final_script}",
            ),
        ]
    )
    chain = prompt | ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=0.7,
    ) | StrOutputParser()
    caption = chain.invoke(
        {
            "topic": state.get("topic", ""),
            "short_description": state.get("short_description", ""),
            "final_script": state.get("final_script", ""),
        }
    ).strip()
    if not caption:
        raise ValueError("Caption generation returned an empty result.")

    caption_path = _save_caption(caption, sorted(videos)[0])
    print(f"Saved caption to {caption_path}")

    return {"caption": caption}


create_captions = create_caption