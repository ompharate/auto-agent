from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv
from graph import create_agent_graph
from state import AgentState
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_graph = create_agent_graph()


@app.get("/")
async def root():
    return {"message": "Auto-agent"}


@app.post("/api/process")
async def process_request(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    pdf: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None)
):
    image_data = await image.read() if image else None
    pdf_data = await pdf.read() if pdf else None
    audio_data = await audio.read() if audio else None

    initial_state: AgentState = {
        "text_input": text,
        "image_data": image_data,
        "pdf_data": pdf_data,
        "audio_data": audio_data,
        "extracted_text": "",
        "plan": [],
        "task": None,
        "needs_clarification": False,
        "clarification_question": None,
        "final_result": None,
        "is_youtube": False,
        "cached_extraction": None,
    }
    
    try:
        logger.info(f"Processing request - Text: {bool(text)}, Image: {bool(image)}, PDF: {bool(pdf)}, Audio: {bool(audio)}")
        final_state = agent_graph.invoke(initial_state)
        
        response = {
            "extracted_text": final_state.get("extracted_text"),
            "plan": final_state.get("plan", []),
            "task": final_state.get("task"),
            "final_result": final_state.get("final_result"),
            "clarification_question": final_state.get("clarification_question"),
        }
        
        logger.info(f"Request processed successfully - Task: {response.get('task')}")
        return response
        
    except Exception as e:
        logger.error(f"Request processing failed: {str(e)}")
        file_type = "audio" if audio else "PDF" if pdf else "image" if image else "text input"
        error_message = f"Failed to process {file_type}. "
        
        if "API" in str(e) or "quota" in str(e).lower():
            error_message += "API service error - please check your API key and quota."
        elif "whisper" in str(e).lower():
            error_message += "Audio transcription failed - ensure Whisper model is installed."
        elif "youtube" in str(e).lower():
            error_message += "YouTube transcript unavailable - video may not have captions."
        else:
            error_message += f"Error: {str(e)}"
        
        return {
            "extracted_text": text or f"[{file_type}]",
            "plan": [],
            "task": "error",
            "final_result": error_message,
            "clarification_question": None,
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
