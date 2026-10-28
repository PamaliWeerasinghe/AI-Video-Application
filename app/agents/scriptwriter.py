import re
from pathlib import Path

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.videoState import VideoState

SCRIPT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _save_script(topic: str, script: str) -> Path:
    safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", topic).strip(" .")
    if not safe_title:
        raise ValueError("The niche title cannot be used as a filename.")
    if re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$", safe_title, re.IGNORECASE):
        safe_title = f"_{safe_title}"

    SCRIPT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    script_path = SCRIPT_OUTPUT_DIR / f"{safe_title}.txt"
    with script_path.open("a+", encoding="utf-8") as script_file:
        script_file.seek(0, 2)
        if script_file.tell() > 0:
            script_file.write("\n\n---\n\n")
        script_file.write(script.strip())
        script_file.write("\n")

    return script_path


def scriptwriter(state: VideoState):
    #Read the topic, writes the script
    topic = state.get("topic", "No topic found")
    # print(f"Scriptwriter: Writing script for topic: {topic}")
    description = state.get("short_description", "No description found")

    #LLM Initialization
    llm = ChatGroq(
        model_name="openai/gpt-oss-120b", 
        temperature=0.7
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an elite viral scriptwriter for Facebook Reels and TikTok.
        Your goal is to write high-retention, engaging scripts designed for monetization.
        
        Always format your scripts strictly into three sections:
        [HOOK]: A compelling 3-second opening to stop the scroll.
        [BODY]: The core value proposition, keeping it fast-paced.
        [CTA]: A smooth, satisfying conclusion that seamlessly resolves the topic and completes the visual flow. Do NOT include any explicit 
        requests to like, follow, comment, or subscribe."""),
        
        ("user", "Write a 60-second video script about this specific topic: {topic}")
    ])
    chain = prompt | llm | StrOutputParser()
    generated_script = chain.invoke({"topic": f"{topic} - {description}"})

    script_path = _save_script(topic, generated_script)
    # print(f"Scriptwriter: Saved script to {script_path}")

    return {"final_script": generated_script}
