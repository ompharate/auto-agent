from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv
from graph import create_agent_graph
from state import AgentState

load_dotenv()

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
        final_state = agent_graph.invoke(initial_state)
        
        response = {
            "extracted_text": final_state.get("extracted_text"),
            "plan": final_state.get("plan", []),
            "task": final_state.get("task"),
            "final_result": final_state.get("final_result"),
            "clarification_question": final_state.get("clarification_question"),
        }
        
        return response
        
    except Exception as e:
        file_type = "Audio" if audio else "PDF" if pdf else "Image" if image else "Text"
        return {
            "extracted_text": text or f"[{file_type}]",
            "plan": [],
            "task": "error",
            "final_result": f"An error occurred: {str(e)}",
            "clarification_question": None,
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
