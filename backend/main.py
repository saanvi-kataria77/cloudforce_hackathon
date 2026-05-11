import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# 1. The NEW, officially supported Google GenAI SDK
from google import genai

from schemas import AnalysisResponse
from services.youtube import get_video_id, get_transcript

load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key not found! Check your .env file.")

# 2. Initialize the modern client
client = genai.Client(api_key=api_key)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Cloudforce Hackathon API is Live!", "docs": "Go to /docs to test"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(url: str):
    video_id = get_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
    transcript = get_transcript(video_id)
    if "Error:" in transcript:
        raise HTTPException(status_code=500, detail=transcript)

    # --- NEW SDK AI CALL 1: Summaries ---
    summary_prompt = f"""
    You are an academic tutor. Summarize this lecture transcript: {transcript}
    Provide the output clearly labeled as:
    QUICK_NOTES: [90-second summary]
    DEEP_DIVE: [5-minute summary]
    FULL_PAGE_NOTES: [Comprehensive notes]
    """
    
    # 3. The new syntax for calling the model
    summary_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=summary_prompt
    )
    raw_summaries = summary_response.text

    # --- NEW SDK AI CALL 2: Audit ---
    audit_prompt = f"""
    You are a Policy Auditor. Analyze this educational transcript: {transcript}
    Look for sociotechnical implications, bias, accessibility gaps, 
    as well as different dimensions of equity and clarity.
    Provide the output clearly labeled as:
    EQUITY: [Equity report]
    ACCESSIBILITY: [Accessibility check]
    BIAS: [Bias analysis]
    """
    
    audit_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=audit_prompt
    )
    raw_audit = audit_response.text

    # Return structured data
    return {
        "video_id": video_id,
        "summaries": {
            "quick_notes": f"Generated Pitch: {raw_summaries[:150]}...",
            "deep_dive": "Generated Deep Dive...",
            "full_page_notes": "Generated Full Notes..."
        },
        "audit": {
            "equity_report": f"Generated Equity Report: {raw_audit[:150]}...",
            "accessibility_check": "Generated Accessibility Check...",
            "bias_analysis": "Generated Bias Analysis..."
        }
    }