from __future__ import annotations

import operator
import asyncio
import os
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, TypedDict, List

import edge_tts
import torch
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
from diffusers import LTXPipeline
from diffusers.utils import export_to_video
from langchain_groq import ChatGroq

from pydantic import BaseModel
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

if TYPE_CHECKING:
    from app.videoState import VideoState

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"

# --- 1. Load Local Video Model (Loaded ONCE globally to save VRAM) ---
print("Loading LTX-Video model into VRAM... This may take a minute.")
try:
    video_pipe = LTXPipeline.from_pretrained(
        "Lightricks/LTX-Video", 
        torch_dtype=torch.bfloat16
    )
    # Enable memory saving features if you have < 24GB VRAM
    video_pipe.enable_model_cpu_offload() 
    # Alternatively, use video_pipe.to("cuda") if you have massive VRAM
except Exception as e:
    print(f"Error loading model: {e}. Ensure you have PyTorch and Diffusers installed.")
    video_pipe = None


# --- 2. Schema Definitions ---
class Scene(BaseModel):
    scene_number: int
    duration: int
    visual_prompt: str
    tts_audio: str
    transition: str

class Storyboard(BaseModel):
    scenes: List[Scene]
    cta_text: str

class DirectorState(TypedDict):
    script: str
    messages: Annotated[list[AnyMessage], add_messages]
    storyboard: Storyboard
    local_clips: Annotated[list[str], operator.add]
    local_audio: Annotated[list[str], operator.add]

# --- 3. Phase 1: Script Parsing ---
def storyboard_node(state: DirectorState):
    script = state["script"]
    
    llm = ChatGroq(
            model_name="llama-3.3-70b-versatile", # Updated to a fast Groq model
            temperature=0.7
    )
    
    structured_llm = llm.with_structured_output(Storyboard)
    
    prompt = f"Parse the following video script into a structured storyboard:\n\n{script}"
    parsed_storyboard = structured_llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "storyboard": parsed_storyboard,
        "messages": [("ai", "Script parsed. Starting local generation.")]
    }

# --- 4. Local Generation Functions ---
async def generate_video_local(prompt: str, scene_num: int) -> str:
    """Runs LTX-Video locally using Diffusers."""
    if not video_pipe:
        raise RuntimeError("Video pipeline failed to load.")
        
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / f"scene_{scene_num}.mp4"
    
    def _run_diffusers():
        print(f"⏳ [Scene {scene_num}] Rendering locally on GPU. Please wait...")
        
        # Generation configuration for LTX-Video
        # Note: LTX-Video works best at specific resolutions (e.g., 704x256, 512x512)
        # Frames must be in specific increments (e.g., 161 frames = ~6 seconds)
        output = video_pipe(
            prompt=prompt,
            negative_prompt="worst quality, inconsistent, blurry, deformed",
            width=704,
            height=256,
            num_frames=161,
            num_inference_steps=50,
        ).frames[0]
        
        print(f"📥 [Scene {scene_num}] Render complete! Exporting to MP4...")
        export_to_video(output, str(filepath), fps=24)
        print(f"✅ [Scene {scene_num}] Saved successfully to {filepath}")
            
    # Run the heavily blocking PyTorch code in a background thread
    await asyncio.to_thread(_run_diffusers)
    return str(filepath)

async def generate_audio_local(text: str, scene_num: int) -> str:
    """Generates high-quality TTS using Microsoft Edge's free neural voices."""
    if not text or text.strip() == "":
        return ""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / f"audio_{scene_num}.mp3"
    
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(str(filepath))
    
    return str(filepath)

# --- 5. Phase 2 Execution Node ---
async def render_tools_node(state: DirectorState):
    storyboard = state["storyboard"]
    new_clips = []
    new_audio = []
    
    # CRITICAL CHANGE: Video generation must be sequential. 
    # GPUs cannot handle parallel video generation without running out of VRAM.
    for scene in storyboard.scenes:
        print(f"Generating assets for Scene {scene.scene_number}...")
        
        # Audio is lightweight, we can await it concurrently with the video thread
        video_task = generate_video_local(scene.visual_prompt, scene.scene_number)
        audio_task = generate_audio_local(scene.tts_audio, scene.scene_number)
        
        video_path, audio_path = await asyncio.gather(video_task, audio_task)
        
        new_clips.append(video_path)
        if audio_path:
            new_audio.append(audio_path)
        
    return {
        "local_clips": new_clips,
        "local_audio": new_audio
    }

# --- 6. Graph Construction ---
director_builder = StateGraph(DirectorState)

director_builder.add_node("storyboard", storyboard_node)
director_builder.add_node("render_tools", render_tools_node) 

director_builder.set_entry_point("storyboard")
director_builder.add_edge("storyboard", "render_tools")
director_builder.add_edge("render_tools", END)

director_subgraph = director_builder.compile()

async def call_director_subgraph(state: VideoState):
    director_input = {
        "script": state["final_script"],
        "messages": [],
        "local_clips": [],
        "local_audio": [],
    }
    
    subgraph_result = await director_subgraph.ainvoke(director_input)
    
    return {
        "video_file_paths": subgraph_result.get("local_clips", []),
        "audio_file_paths": subgraph_result.get("local_audio", [])
    }