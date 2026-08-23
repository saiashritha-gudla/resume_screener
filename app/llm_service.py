"""
LLM service using Groq.

Responsibilities:
1. Extract structured candidate information from resumes.
2. Compare a candidate with a job description.
3. Produce a consistent 1-10 match score.
"""

import os
import json

from groq import Groq
from dotenv import load_dotenv

from app.schemas import CandidateProfile, MatchResult


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing from the .env file."
    )

client = Groq(api_key=api_key)

# Current Groq model
MODEL = "openai/gpt-oss-120b"


# =========================================================
# GENERIC GROQ CALL
# =========================================================

def _call_llm(prompt: str) -> str:
    """
    Send a prompt to Groq and return the text response.
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_completion_tokens=1500,
        reasoning_effort="low"
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "Groq returned an empty response."
        )

    return content.strip()


# =========================================================
# JSON CLEANING
# =========================================================

def _clean_json(text: str) -> dict:
    """
    Remove markdown code fences if the model returns them,
    then convert the response into a Python dictionary.
    """

    text = text.strip()

    # Handle:
    #
    # ```json
    # {...}
    # ```

    if text.startswith("```"):

        parts = text.split("```")

        if len(parts) >= 2:
            text = parts[1].strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    try:

        return json.loads(text)

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            f"LLM returned invalid JSON.\n\n"
            f"Response:\n{text}"
        ) from exc


# =========================================================
# RESUME EXTRACTION PROMPT
# =========================================================

EXTRACTION_PROMPT = """
You are a resume parsing assistant.

Read the resume below and extract structured information.

IMPORTANT RULES:

1. Use ONLY information explicitly present in the resume.
2. Never invent skills, experience, education, companies,
   projects or achievements.
3. Skills can include technologies, programming languages,
   frameworks, libraries, databases and tools explicitly mentioned.
4. Experience can include internships, jobs, projects or
   other relevant practical experience explicitly mentioned.
5. Projects should be treated as practical experience.
6. Education should contain degree, specialization,
   institution, graduation year and CGPA if explicitly present.
7. Keep experience entries concise.
8. Keep education entries concise.
9. If a field is not present, return an empty string or empty list.
10. Return valid JSON only.

Resume:

{resume_text}

Return ONLY valid JSON using exactly this structure:

{{
    "name": "",
    "email": "",
    "phone": "",
    "skills": [],
    "experience": [],
    "education": []
}}
"""


# =========================================================
# NORMALIZE SKILLS
# =========================================================

def _normalize_skills(data: dict) -> list[str]:
    """
    Make sure skills is always a list of strings.
    """

    skills = data.get("skills", [])

    if not isinstance(skills, list):
        return []

    normalized = []

    for skill in skills:

        if isinstance(skill, str):
            normalized.append(skill)

        elif isinstance(skill, dict):

            # Convert unexpected dictionary values
            # into readable text.
            parts = []

            for key, value in skill.items():

                if value:
                    parts.append(
                        f"{key}: {value}"
                    )

            if parts:
                normalized.append(
                    ", ".join(parts)
                )

        else:
            normalized.append(str(skill))

    return normalized


# =========================================================
# NORMALIZE EXPERIENCE
# =========================================================

def _normalize_experience(data: dict) -> list[str]:
    """
    Make sure experience is always a list of strings.

    The LLM may return either:

    [
        "Built an ML model..."
    ]

    or:

    [
        {
            "company": "...",
            "role": "...",
            "description": "..."
        }
    ]

    Our CandidateProfile expects strings,
    so dictionaries are converted to readable strings.
    """

    experience = data.get("experience", [])

    if not isinstance(experience, list):
        return []

    normalized = []

    for item in experience:

        # Already a string
        if isinstance(item, str):

            normalized.append(item)

        # Dictionary returned by LLM
        elif isinstance(item, dict):

            parts = []

            for key, value in item.items():

                if value:
                    parts.append(
                        f"{key}: {value}"
                    )

            if parts:
                normalized.append(
                    ", ".join(parts)
                )

        # Any other unexpected value
        else:

            normalized.append(
                str(item)
            )

    return normalized


# =========================================================
# NORMALIZE EDUCATION
# =========================================================

def _normalize_education(data: dict) -> list[str]:
    """
    Make sure education is always a list of strings.

    The LLM may return:

    [
        {
            "degree": "B.Tech",
            "specialization": "AI & ML",
            "institution": "VIT-AP",
            "graduation_year": "2027",
            "cgpa": "7.6"
        }
    ]

    CandidateProfile expects:

    education: list[str]

    Therefore the dictionary is converted into a readable string.
    """

    education = data.get("education", [])

    if not isinstance(education, list):
        return []

    normalized = []

    for item in education:

        # Already a string
        if isinstance(item, str):

            normalized.append(item)

        # Dictionary returned by LLM
        elif isinstance(item, dict):

            parts = []

            # Keep the most useful fields in a sensible order
            preferred_keys = [
                "degree",
                "specialization",
                "institution",
                "graduation_year",
                "cgpa"
            ]

            for key in preferred_keys:

                value = item.get(key)

                if value:
                    parts.append(
                        f"{key}: {value}"
                    )

            # Include any additional fields
            for key, value in item.items():

                if key not in preferred_keys and value:

                    parts.append(
                        f"{key}: {value}"
                    )

            if parts:
                normalized.append(
                    ", ".join(parts)
                )

        # Any other unexpected value
        else:

            normalized.append(
                str(item)
            )

    return normalized


# =========================================================
# EXTRACT CANDIDATE PROFILE
# =========================================================

def extract_candidate_profile(
    resume_text: str
) -> CandidateProfile:
    """
    Extract structured candidate information from resume text.
    """

    prompt = EXTRACTION_PROMPT.format(
        resume_text=resume_text
    )

    # Call Groq
    raw = _call_llm(prompt)

    # Convert JSON response to dictionary
    data = _clean_json(raw)

    # Normalize fields
    skills = _normalize_skills(data)

    experience = _normalize_experience(data)

    education = _normalize_education(data)

    # Create Pydantic CandidateProfile
    return CandidateProfile(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        skills=skills,
        experience=experience,
        education=education
    )


# =========================================================
# MATCHING PROMPT
# =========================================================

MATCH_PROMPT = """
You are an objective resume screening assistant.

Compare the candidate profile with the job description.

Candidate profile:

{candidate_profile}

Job description:

{job_description}

Evaluate the candidate using ONLY evidence present in the
candidate profile and job description.

Scoring guidelines:

10 = Exceptional match
9  = Very strong match
8  = Strong match
7  = Good match
6  = Moderate match
5  = Partial match
4  = Weak match
3  = Poor match
2  = Very poor match
1  = Almost no match

Consider these factors:

1. Required technical skills
2. Relevant experience
3. Relevant projects
4. Education relevance
5. Overall alignment with the job

IMPORTANT:

- Do NOT reject a candidate simply because a preferred skill
  is missing.
- Do NOT claim that a skill is missing if it is explicitly present.
- Treat projects as valid evidence of practical experience.
- Use the candidate's complete profile.
- Do not invent experience.
- Do not consider age, gender, ethnicity, religion, nationality,
  disability, marital status or other protected characteristics.
- Base the score only on evidence from the resume and job description.
- Distinguish between required skills and preferred skills.
- Give reasonable credit for closely related technologies.

Recommendation rules:

Shortlist = score >= 7
Review = score >= 5 and < 7
Reject = score < 5

Return ONLY valid JSON using exactly this structure:

{{
    "match_score": 0,
    "matching_skills": [],
    "missing_skills": [],
    "recommendation": "Shortlist|Review|Reject",
    "justification": ""
}}

The justification must briefly explain WHY the score was given.
"""


# =========================================================
# COMPUTE MATCH
# =========================================================

def compute_match(
    candidate: CandidateProfile,
    job_description_text: str
) -> MatchResult:
    """
    Compare a candidate with a job description
    and produce a 1-10 match score.
    """

    candidate_profile = candidate.model_dump_json()

    prompt = MATCH_PROMPT.format(
        candidate_profile=candidate_profile,
        job_description=job_description_text
    )

    # Call Groq
    raw = _call_llm(prompt)

    # Parse JSON
    data = _clean_json(raw)

    # =====================================================
    # Normalize score
    # =====================================================

    try:

        score = float(
            data.get("match_score", 0)
        )

    except (ValueError, TypeError):

        score = 0

    # Keep score between 1 and 10
    score = max(
        1.0,
        min(score, 10.0)
    )

    # Round to one decimal
    score = round(
        score,
        1
    )

    # =====================================================
    # Force recommendation
    # =====================================================

    if score >= 7:

        recommendation = "Shortlist"

    elif score >= 5:

        recommendation = "Review"

    else:

        recommendation = "Reject"

    # =====================================================
    # Normalize matching skills
    # =====================================================

    matching_skills = data.get(
        "matching_skills",
        []
    )

    if not isinstance(
        matching_skills,
        list
    ):
        matching_skills = []

    matching_skills = [
        str(skill)
        for skill in matching_skills
    ]

    # =====================================================
    # Normalize missing skills
    # =====================================================

    missing_skills = data.get(
        "missing_skills",
        []
    )

    if not isinstance(
        missing_skills,
        list
    ):
        missing_skills = []

    missing_skills = [
        str(skill)
        for skill in missing_skills
    ]

    # =====================================================
    # Justification
    # =====================================================

    justification = data.get(
        "justification",
        "No justification provided."
    )

    if not isinstance(
        justification,
        str
    ):
        justification = str(
            justification
        )

    # =====================================================
    # Final MatchResult
    # =====================================================

    return MatchResult(
        candidate_name=candidate.name,

        match_score=score,

        justification=justification,

        matching_skills=matching_skills,

        missing_skills=missing_skills,

        recommendation=recommendation
    )