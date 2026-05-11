from pydantic import BaseModel, ValidationError, field_validator

class LectureSummaries(BaseModel):
    quick_notes: str
    deep_dive: str
    full_page_notes: str

class FacultyAudit(BaseModel):
    equity_report: str
    accessibility_check: str
    bias_analysis: str

class AnalysisResponse(BaseModel):
    video_id: str
    summaries: LectureSummaries
    audit: FacultyAudit

