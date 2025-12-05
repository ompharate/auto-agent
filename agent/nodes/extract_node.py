from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pdf2image import convert_from_bytes
from youtube_transcript_api import YouTubeTranscriptApi
import pdfplumber
import base64
import io
import re
from state import AgentState
import whisper
import tempfile
import os
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_youtube_video_id(text: str):
    """Extract YouTube video ID."""
    if not text:
        return None

    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"v=([a-zA-Z0-9_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def gemini_ocr_image(image_bytes: bytes) -> str:
    """Use Gemini 2.5 Flash Vision for OCR on image."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Extract ALL text exactly as it appears. Return ONLY the raw extracted text."},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}
        ]
    )

    response = llm.invoke([message])
    return response.content.strip()


def extract_node(state: AgentState) -> AgentState:
    """Extract text from all input types: text, YouTube, image, PDF, and audio."""
    
    text_input = state.get("text_input")
    image_data = state.get("image_data")
    pdf_data = state.get("pdf_data")
    audio_data = state.get("audio_data")
    cached_extraction = state.get("cached_extraction")
    extracted_text = ""
    
    # If we have cached extraction from previous file and files are present, use cache
    if cached_extraction and (image_data or pdf_data or audio_data):
        logger.info("Using cached file extraction")
        if text_input:
            extracted_text = f"{cached_extraction}\n\n[User clarification]: {text_input}"
        else:
            extracted_text = cached_extraction
        return {**state, "extracted_text": extracted_text}

    # Check for YouTube URL first
    video_id = extract_youtube_video_id(text_input)
    if video_id:
        try:
            logger.info(f"Fetching YouTube transcript for video ID: {video_id}")
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
            combined = " ".join([t.text for t in transcript])
            logger.info(f"YouTube transcript fetched successfully: {len(combined)} characters")
            extracted_text = f"[YouTube Video Transcript]\n\n{combined}"
        except Exception as e:
            logger.error(f"YouTube transcript fetch failed: {str(e)}")
            extracted_text = "[Error: Cannot fetch YouTube transcript — no captions available or invalid URL]"
        return {**state, "extracted_text": extracted_text, "is_youtube": True, "cached_extraction": extracted_text}

    if text_input:
        extracted_text = text_input

    # Extract text from image using Gemini Vision
    if image_data:
        try:
            logger.info("Processing image with Gemini Vision OCR")
            image_text = gemini_ocr_image(image_data)
            logger.info(f"Image OCR completed: {len(image_text)} characters extracted")
            if extracted_text:
                extracted_text += f"\n\n[Image OCR]\n{image_text}"
            else:
                extracted_text = image_text
        except Exception as e:
            logger.error(f"Image OCR failed: {str(e)}")
            extracted_text += f"\n[Image OCR Error: Failed to process image - {str(e)}]"

    # Extract text from PDF (try digital text first, fallback to OCR)
    if pdf_data:
        pdf_text = ""
        try:
            with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
                for i, page in enumerate(pdf.pages):
                    txt = page.extract_text() or ""
                    pdf_text += f"\n--- Page {i+1} ---\n{txt}"
        except:
            pdf_text = ""

        if not pdf_text.strip():
            try:
                logger.info("PDF appears to be scanned, using Gemini Vision OCR")
                images = convert_from_bytes(pdf_data)
                logger.info(f"Processing {len(images)} PDF pages with OCR")
                ocr_text = ""
                for i, img in enumerate(images):
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="PNG")
                    page_text = gemini_ocr_image(img_buffer.getvalue())
                    ocr_text += f"\n--- Page {i+1} (OCR) ---\n{page_text}"
                pdf_text = ocr_text
                logger.info(f"PDF OCR completed: {len(pdf_text)} characters extracted")
            except Exception as e:
                logger.error(f"PDF OCR failed: {str(e)}")
                pdf_text = f"[PDF OCR Error: Failed to process scanned PDF - {str(e)}]"

        if extracted_text:
            extracted_text += f"\n\n[PDF Content]\n{pdf_text}"
        else:
            extracted_text = pdf_text

    # Transcribe audio using Whisper
    if audio_data:
        try:
            logger.info("Transcribing audio with Whisper (base model)")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_data)
                temp_path = temp_audio.name

            model = whisper.load_model("base")
            result = model.transcribe(temp_path)
            audio_text = result.get("text", "").strip()
            os.unlink(temp_path)
            logger.info(f"Audio transcription completed: {len(audio_text)} characters")

            if extracted_text:
                extracted_text += f"\n\n[Audio Transcript]\n{audio_text}"
            else:
                extracted_text = audio_text
        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            extracted_text += f"[Audio Error: Failed to transcribe audio - {str(e)}]"

    final_text = extracted_text.strip() if extracted_text else "[No input detected]"
    
    # Cache extraction if we processed files (not just text input)
    should_cache = bool(image_data or pdf_data or audio_data)
    
    return {
        **state,
        "extracted_text": final_text,
        "cached_extraction": final_text if should_cache else cached_extraction
    }
