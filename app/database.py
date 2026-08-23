"""
Database storage for parsed resumes, job descriptions, and match results.
(PPT requirement: "Database storage for parsed resumes")
"""
import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_screener.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class ResumeRecord(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    raw_text = Column(Text)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    skills = Column(Text)        # stored as JSON string
    experience = Column(Text)    # stored as JSON string
    education = Column(Text)     # stored as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class JobRecord(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class MatchRecord(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer)
    job_id = Column(Integer)
    candidate_name = Column(String, nullable=True)
    match_score = Column(Float)
    justification = Column(Text)
    matching_skills = Column(Text)   # JSON string
    missing_skills = Column(Text)    # JSON string
    recommendation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def to_json(value: list) -> str:
    return json.dumps(value or [])


def from_json(value: str) -> list:
    return json.loads(value) if value else []
