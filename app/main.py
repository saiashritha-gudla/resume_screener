"""
Backend API for the Smart Resume Screener.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import (
    init_db,
    get_db,
    ResumeRecord,
    JobRecord,
    MatchRecord,
    to_json,
    from_json,
)

from app.extraction import extract_text
from app.llm_service import extract_candidate_profile, compute_match
from app.schemas import JobDescriptionInput, CandidateProfile, MatchResult


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(title="Smart Resume Screener")


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

@app.on_event("startup")
def on_startup():
    init_db()


# ---------------------------------------------------------
# Upload Resume
# ---------------------------------------------------------

@app.post("/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_bytes = await file.read()

    try:
        raw_text = extract_text(
            file.filename,
            file_bytes
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not raw_text:
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from this file."
        )

    try:
        profile = extract_candidate_profile(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM extraction failed: {str(e)}"
        )

    record = ResumeRecord(
        filename=file.filename,
        raw_text=raw_text,
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        skills=to_json(profile.skills),
        experience=to_json(profile.experience),
        education=to_json(profile.education),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "resume_id": record.id,
        "profile": profile
    }


# ---------------------------------------------------------
# Create Job
# ---------------------------------------------------------

@app.post("/jobs")
def create_job(
    job: JobDescriptionInput,
    db: Session = Depends(get_db)
):
    record = JobRecord(
        title=job.title,
        description_text=job.description_text
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "job_id": record.id
    }


# ---------------------------------------------------------
# Match Candidate
# ---------------------------------------------------------

@app.post("/match")
def match_candidate(
    resume_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    resume = (
        db.query(ResumeRecord)
        .filter(ResumeRecord.id == resume_id)
        .first()
    )

    job = (
        db.query(JobRecord)
        .filter(JobRecord.id == job_id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job description not found."
        )

    profile = CandidateProfile(
        name=resume.name,
        email=resume.email,
        phone=resume.phone,
        skills=from_json(resume.skills),
        experience=from_json(resume.experience),
        education=from_json(resume.education),
    )

    try:
        result: MatchResult = compute_match(
            profile,
            job.description_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM matching failed: {str(e)}"
        )

    record = MatchRecord(
        resume_id=resume_id,
        job_id=job_id,
        candidate_name=result.candidate_name,
        match_score=result.match_score,
        justification=result.justification,
        matching_skills=to_json(result.matching_skills),
        missing_skills=to_json(result.missing_skills),
        recommendation=result.recommendation,
    )

    db.add(record)
    db.commit()

    return result


# ---------------------------------------------------------
# Ranked Candidates
# ---------------------------------------------------------

@app.get("/candidates/{job_id}")
def list_candidates_for_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Return all evaluated candidates for a job,
    ranked by match score from highest to lowest.
    """

    matches = (
        db.query(MatchRecord)
        .filter(MatchRecord.job_id == job_id)
        .order_by(MatchRecord.match_score.desc())
        .all()
    )

    return [
        {
            "candidate_name": m.candidate_name,
            "match_score": m.match_score,
            "recommendation": m.recommendation,
            "justification": m.justification,
            "matching_skills": from_json(m.matching_skills),
            "missing_skills": from_json(m.missing_skills),
        }
        for m in matches
    ]


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "Smart Resume Screener API is running"
    }