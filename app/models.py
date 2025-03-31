from pydantic import BaseModel

class MessageRequest(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    headline: str
    gemini_summary: str