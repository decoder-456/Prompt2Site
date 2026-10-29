from typing import TypedDict
from pydantic import BaseModel, Field

class AgentState(TypedDict, total=False):
    requirement: str
    plan: str
    design_spec: str
    html: str
    css: str
    javascript: str
    test_report: str
    passed: bool
    attempts: int
    approved: bool
    human_feedback: str
    error_signature: str
    error_history: list[str]

class WebsiteFiles(BaseModel):
    html: str = Field(description="Complete index.html source")
    css: str = Field(description="Complete style.css source")
    javascript: str = Field(description="Complete script.js source")

class ReviewResult(BaseModel):
    passed: bool = Field(description="Whether website passes review")
    review: str = Field(description="Specific findings and repair instructions")

class StartRequest(BaseModel):
    requirement: str

class ResumeRequest(BaseModel):
    action: str
    feedback: str = ""
