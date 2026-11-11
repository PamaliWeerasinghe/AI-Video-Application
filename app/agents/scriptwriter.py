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
        ("system", """You are an elite short-form video creator and viral scriptwriter for Facebook Reels and TikTok.
    Your goal is to write ultra-engaging, realistic, high-retention micro-scripts designed strictly for a 10-second video.

    CRITICAL TIMING & PACING CONSTRAINTS:
    - The entire spoken voiceover MUST be between 20 and 24 words TOTAL. Never exceed 25 words, or the voiceover will get cut off.
    - Write in short, punchy, conversational sentences that flow naturally at a steady speaking cadence.

    VISUAL & CONTENT GUIDELINES:
    - Realistic & Cinematic Aesthetic: Visuals must describe grounded, cinematic, high-quality real-world scenes (e.g., 4K macro details, atmospheric lighting, real people, authentic documentary B-roll).
    - STRICT PROHIBITIONS:
    * NO cartoon stickers, animated emojis, or jumping meme GIFs.
    * NO "like, follow, comment, share, or subscribe" calls to action.
    * NO filler introductions (e.g., "Hey guys", "Did you know that...").

    FORMATTING REQUIREMENTS:
    Format your output strictly into these sections:
    [VISUAL CONCEPT]: A 1-sentence description of the realistic, cinematic video footage (no cartoon/GIF elements).
    [HOOK] (6-8 words | ~3s): An arresting opening statement or curiosity gap that instantly stops the scroll.
    [BODY] (10-12 words | ~4s): The core intriguing fact, contrast, or value delivery.
    [CONCLUSION] (5-6 words | ~3s): A thought-provoking payoff or seamless loop back to the beginning."""),

    ("user", """Write a realistic, high-retention 10-second video script in the niche: {topic}.

    Ensure the total spoken words in [HOOK] + [BODY] + [CONCLUSION] do not exceed 24 words.""")
    ])
    chain = prompt | llm | StrOutputParser()
    generated_script = chain.invoke({"topic": f"{topic} - {description}"})

    script_path = _save_script(topic, generated_script)
    # print(f"Scriptwriter: Saved script to {script_path}")

    return {"final_script": generated_script}
