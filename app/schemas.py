"""
Pydantic models used across the app.

CandidateProfile mirrors the PPT requirement:
  "Extract structured data: skills, experience, education"

MatchResult mirrors the PPT requirement:
  "Use LLM to compute a match score between candidate and job description"
  "Display shortlisted candidates with justification"
"""
from pydantic import BaseModel
from typing import Optional


class CandidateProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: list[str] = []
    experience: list[str] = []   # short text entries, e.g. "Backend Developer at XYZ (2 yrs)"
    education: list[str] = []    # short text entries, e.g. "B.Tech in CS, ABC University, 2022"


class JobDescriptionInput(BaseModel):
    title: str
    description_text: str


class MatchResult(BaseModel):
    candidate_name: Optional[str]
    match_score: float          # 1-10, per PPT
    justification: str          # per PPT: "rate fit on 1-10 with justification"
    matching_skills: list[str] = []
    missing_skills: list[str] = []
    recommendation: str         # Shortlist | Review | Reject
