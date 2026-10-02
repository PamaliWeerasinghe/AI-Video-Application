import operator
from typing import Annotated, TypedDict, List, Dict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Standard fields where the last writer overwrites the value
    topic: str
    script: str
    audio_file_path: str
    
    # QA Report stores the pass/fail status and reasoning
    qa_report: Dict[str, str] 
    
    # Annotated fields use reducers to merge data instead of overwriting
    # operator.add ensures new video clips are appended to the list
    video_file_paths: Annotated[List[str], operator.add]
    
    # add_messages appends new LLM messages to the ongoing conversation history
    messages: Annotated[List[AnyMessage], add_messages]