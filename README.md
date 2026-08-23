# Smart Resume Screener

An AI-powered resume screening application that parses resumes, matches candidates against job descriptions, identifies skill gaps, and generates evidence-based shortlisting recommendations using an LLM.

**Live App:** [Streamlit Dashboard](https://resumescreener-mwverpp2hbzv2wsqxu9yua.streamlit.app/) · [API Docs (Swagger)](https://resume-screener-977g.onrender.com/docs) · [Backend](https://resume-screener-977g.onrender.com)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Running Locally](#running-locally)
- [Deployment](#deployment)
- [Security](#security)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Overview

Smart Resume Screener helps recruiters evaluate candidates consistently by transforming unstructured resumes into structured profiles and comparing them against job requirements using an LLM (Groq / Llama 3.3 70B). It returns a 1–10 match score, identifies matching skills and skill gaps, and produces a Shortlist / Review / Reject recommendation with a written justification — reducing manual screening time while keeping the final decision with a human reviewer.

## Features

- Resume upload and parsing (PDF and TXT)
- AI-powered extraction of name, email, phone, skills, experience, and education
- Job description creation and storage
- AI-powered candidate-to-job matching
- Consistent 1–10 match scoring
- Matching skill identification and skill-gap analysis
- Project/experience evidence considered during skill-gap analysis (not just keyword matching)
- AI-generated written justification for each evaluation
- Automatic Shortlist / Review / Reject recommendation
- Ranked candidate shortlist per job
- FastAPI backend with interactive Swagger documentation
- Streamlit recruiter dashboard with a cream-and-navy professional theme
- SQLite persistence for resumes, jobs, and match results

## Architecture

```text
                ┌───────────────────────┐
                │   Streamlit Dashboard  │
                │   (Recruiter UI)       │
                └───────────┬────────────┘
                             │  REST API
                             ▼
                ┌───────────────────────┐
                │    FastAPI Backend     │
                └───────────┬────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                   ▼
   ┌─────────────┐   ┌───────────────┐   ┌──────────────┐
   │  Resume      │   │  Groq LLM     │   │  SQLite DB   │
   │  Extraction  │   │  (Llama 3.3)  │   │              │
   │ (pdfplumber) │   │  Match + Parse│   │  Resumes,    │
   │              │   │               │   │  Jobs,       │
   │              │   │               │   │  Matches     │
   └─────────────┘   └───────────────┘   └──────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, custom CSS |
| Backend | FastAPI, Uvicorn |
| AI / LLM | Groq API, Llama 3.3 70B Versatile |
| Data | SQLAlchemy, SQLite, Pydantic |
| Resume Parsing | pdfplumber |
| Integration | Requests |
| Deployment | Streamlit Community Cloud, Render |

## How It Works

1. **Upload Resume** — Recruiter uploads a PDF or TXT resume; text is extracted via pdfplumber.
2. **AI Parsing** — The LLM extracts structured fields: name, email, phone, skills, experience, education.
3. **Job Description** — Recruiter enters a job title, description, and required skills, which are stored in SQLite.
4. **Evaluation** — The candidate profile is compared against the job description for skill overlap, relevant experience/projects, and education relevance.
5. **Match Score** — A 1–10 score is generated:

   | Score | Interpretation |
   |---|---|
   | 8.0 – 10.0 | Excellent Match |
   | 7.0 – 7.9 | Strong Match |
   | 5.0 – 6.9 | Review |
   | Below 5.0 | Weak Match |

6. **Skill Gap Analysis** — Matching skills and missing skills are identified; relevant projects count as evidence of practical experience.
7. **Recommendation**:

   | Score | Recommendation |
   |---|---|
   | ≥ 7 | Shortlist |
   | 5 – 6.9 | Review |
   | < 5 | Reject |

8. **Ranked Shortlist** — Candidates for a job are ranked by match score in the dashboard.

## Project Structure

```text
resume_screener/
│
├── app/
│   ├── database.py       # SQLAlchemy models, DB session
│   ├── extraction.py     # PDF/TXT text extraction
│   ├── llm_service.py    # Groq LLM calls: parsing + matching
│   ├── main.py            # FastAPI routes
│   └── schemas.py         # Pydantic request/response models
│
├── dashboard/
│   └── streamlit_app.py   # Recruiter-facing dashboard
│
├── requirements.txt
├── .gitignore
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/resumes/upload` | Upload a resume file |
| POST | `/resumes/{resume_id}/parse` | Extract structured candidate data |
| POST | `/jobs` | Create a job description |
| POST | `/match` | Compute candidate-job match |
| GET | `/candidates/{job_id}` | List ranked candidates for a job |

Full interactive documentation is available at `/docs` on the running backend.

## Running Locally

**1. Clone the repository**
```bash
git clone https://github.com/saiashritha-gudla/resume_screener.git
cd resume_screener
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key
```

**5. Start the backend**
```bash
uvicorn app.main:app --reload
```
Runs at `http://127.0.0.1:8000` · Swagger docs at `http://127.0.0.1:8000/docs`

**6. Start the dashboard** (in a separate terminal)
```bash
streamlit run dashboard/streamlit_app.py
```
Runs at `http://localhost:8501`

## Deployment

- **Frontend** — Streamlit Community Cloud
- **Backend** — Render
- The dashboard communicates with the deployed FastAPI backend over REST.

## Security

- API keys are stored as environment variables, never hardcoded.
- `.env` is excluded from version control via `.gitignore`.

## Future Improvements

- Batch resume screening
- Semantic / embedding-based matching
- Vector database integration (RAG-based matching)
- Candidate comparison dashboard
- Recruiter authentication
- Exportable screening reports (PDF/CSV)
- PostgreSQL for production
- Recruitment analytics dashboard

## Disclaimer

This application is an AI-assisted recruitment screening tool. AI-generated scores and recommendations are intended to support, not replace, human judgment in hiring decisions.
