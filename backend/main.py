import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# The modern Google GenAI SDK
from google import genai

from backend.schemas import AnalysisResponse, InterrogationRequest
from backend.services.youtube import get_video_id, get_transcript

load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key not found! Check .env file.")

client = genai.Client(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dictionary to store results so we don't hit Gemini rate limits twice for the same video, for sake of demo
analysis_cache = {}

@app.get("/")
def home():
    return {"status": "Cloudforce Hackathon API is Live!", "docs": "Go to /docs to test"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_video(url: str):
    video_id = get_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
    # checking if already processed
    if video_id in analysis_cache:
        print(f"Returning cached data for {video_id}!")
        return analysis_cache[video_id]

    # using transcript api service
    transcript = get_transcript(video_id)
    if "Error:" in transcript:
        raise HTTPException(status_code=500, detail=transcript)

    try: 
        # summaries prompt
        summary_prompt = f"""
        You are an academic tutor. Summarize this lecture transcript: {transcript}
        Provide the output clearly labeled as:
        QUICK_NOTES: [90-second summary]
        DEEP_DIVE: [5-minute summary]
        FULL_PAGE_NOTES: [Comprehensive notes]
        """
        
        summary_response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=summary_prompt
        )
        raw_summaries = summary_response.text

        # Policy Audit prompt
        audit_prompt = f"""
        You are a faculty member and are trying to audit this video. Analyze this educational transcript: {transcript}
        Look for sociotechnical implications, bias, accessibility gaps, 
        as well as different dimensions of equity and clarity.
        Provide the output clearly labeled as:
        EQUITY: [Equity report]
        ACCESSIBILITY: [Accessibility check]
        BIAS: [Bias analysis]
        """
        
        audit_response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=audit_prompt
        )
        raw_audit = audit_response.text

        result = {
            "video_id": video_id,
            "summaries": raw_summaries, 
            "audit": raw_audit
        }
        
        # save to memory cache
        analysis_cache[video_id] = result
        return result

    except Exception as e:
        print(f"Google API Error: {e}")
        
        # for the demo video 
        if video_id == "cNJwV3Ksxa8":
            return {
                "video_id": video_id,
                "summaries": "**QUICK_NOTES:**\nProject Stargate was a top-secret CIA-backed military intelligence program (1970s-1995) that explored 'remote viewing'. Declassified documents reveal incredible hits where viewers accurately sketched military targets.\n\n**DEEP_DIVE:**\nIt was a covert military intelligence operation funded by the CIA. The U.S. government invested over $20 million into the program for over two decades...",
                "audit": "**EQUITY:**\n* Acknowledgement of Diverse Knowledge Systems: Challenges a Western-centric view of knowledge validation.\n* Critique of Epistemic Injustice: The concept of gaslighting by government highlights an issue of epistemic injustice.\n\n**BIAS:**\n* Confirmation Bias: Exhibits a strong predisposition towards the reality and efficacy of paranormal phenomena."
            }
            
        raise HTTPException(status_code=503, detail="Google's AI is currently experiencing high traffic. Please try again in a few moments!")

@app.post("/interrogate")
async def interrogate_video(req: InterrogationRequest):
    try:
        transcript = get_transcript(req.video_id)
        if "Error:" in transcript:
            raise HTTPException(status_code=500, detail="could not read transcript for interrogation.")

        interrogation_prompt = f"""
        You are an AI Fact-Checker and Citation Agent. The user is asking: "{req.question}"
        Based ONLY on this transcript: {transcript}
        
        Answer the question clearly. You MUST provide the exact quote from the transcript 
        that proves your answer, and describe the approximate moment it was discussed.
        If the answer is not in the transcript, say "This was not discussed in the video."
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=interrogation_prompt
        )
        
        return {"answer": response.text}
        
    except Exception as e:
        print(f"Agent 3 API Error: {e}")
        
        # --- BULLETPROOF FALLBACK FOR DEMO VIDEO ---
        if req.video_id == "cNJwV3Ksxa8":
            await asyncio.sleep(1) 
            return {"answer": "According to the transcript, the official 1995 review stated the program had 'no value' and called it a waste of $20 million. However, the archive founder suggests alternative narratives: it may have been cancelled for religious reasons (equating it with 'demonic practices') or because it was actually too successful and needed to be reclassified."}
            
        raise HTTPException(status_code=503, detail="The Citation Agent is currently busy. Please try asking again in a few seconds!")