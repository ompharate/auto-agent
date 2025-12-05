from typing import TypedDict, Optional, List, Any


class AgentState(TypedDict):
    """State object passed through the agent graph"""
    text_input: Optional[str]
    image_data: Optional[bytes]
    pdf_data: Optional[bytes]
    audio_data: Optional[bytes]
    extracted_text: str
    plan: List[str]
    task: Optional[str] 
    needs_clarification: bool
    clarification_question: Optional[str]
    final_result: Optional[str]
    is_youtube: Optional[bool]
