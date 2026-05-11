from pydantic import BaseModel

class AnalysisResponse(BaseModel):
    video_id: str
    summaries: str  # expects raw, large string 
    audit: str      # expect raw, large string 

class InterrogationRequest(BaseModel):
    video_id: str
    question: str

