"""
Smart Resume Screener
Classic Professional Streamlit Dashboard

Run:
    streamlit run dashboard/streamlit_app.py

Backend:
    uvicorn app.main:app --reload
"""

import html
import re
import requests
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "https://resume-screener-977g.onrender.com"

st.set_page_config(
    page_title="Smart Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    html, body, [class*="css"] {
        font-family: Georgia, "Times New Roman", serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(181, 151, 92, 0.10),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f5efe3 0%,
                #eee4d2 50%,
                #f7f2e8 100%
            );
        color: #29364d;
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .main {
        padding-top: 0;
    }

    /* Remove excessive Streamlit vertical gaps */

    div[data-testid="stVerticalBlock"] {
        gap: 0.45rem;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }

    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background: #eee4d2;
        border-right: 1px solid #d5c3a3;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .sidebar-brand {
        color: #29364d;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 1rem;
        letter-spacing: 0.2px;
    }

    .sidebar-label {
        color: #6f675b;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .sidebar-value {
        color: #29364d;
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
    }

    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        background:
            linear-gradient(
                135deg,
                #202d46 0%,
                #29364d 55%,
                #35445f 100%
            );

        color: #f7f2e8;

        padding: 2rem 2.3rem;
        border-radius: 16px;

        border: 1px solid #b79a68;

        box-shadow:
            0 12px 28px rgba(41, 54, 77, 0.18);

        margin-bottom: 1.4rem;
    }

    .hero-title {
        font-size: 2.45rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #eee4d2;
        line-height: 1.55;
        max-width: 850px;
    }

    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 1rem;
    }

    .hero-pill {
        background: rgba(238, 228, 210, 0.12);
        border: 1px solid rgba(238, 228, 210, 0.35);
        color: #f7f2e8;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 0.76rem;
        font-weight: 700;
    }

    /* =====================================================
       SECTION HEADERS
       ===================================================== */

    .section-title {
        color: #29364d;
        font-size: 1.65rem;
        font-weight: 800;

        border-bottom: 1px solid #d5c3a3;

        padding-bottom: 0.4rem;
        margin-top: 1.3rem;
        margin-bottom: 0.55rem;
    }

    .section-description {
        color: #756d61;
        font-size: 0.92rem;
        margin-bottom: 0.7rem;
        line-height: 1.45;
    }

    /* =====================================================
       CLASSIC CARDS
       ===================================================== */

    .card {
        background: #fbf8f1;
        border: 1px solid #d8c7a8;
        border-radius: 12px;
        padding: 1.05rem 1.15rem;
        margin-bottom: 0.65rem;

        box-shadow:
            0 4px 12px rgba(41, 54, 77, 0.07);
    }

    .card-title {
        color: #29364d;
        font-size: 1.12rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .profile-info {
        color: #4f4a43;
        line-height: 1.65;
        font-family: Arial, sans-serif;
        font-size: 0.92rem;
    }

    .profile-info strong {
        color: #29364d;
    }

    /* =====================================================
       SCORE CARDS
       ===================================================== */

    .score-card {
        background:
            linear-gradient(
                145deg,
                #fbf8f1,
                #f0e5d1
            );

        border: 1px solid #cdb78d;
        border-radius: 12px;

        padding: 1.1rem;

        text-align: center;

        box-shadow:
            0 5px 15px rgba(41, 54, 77, 0.08);
    }

    .score-number {
        color: #8b3850;
        font-size: 3.4rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.35rem;
    }

    .score-label {
        color: #71695e;
        font-size: 0.88rem;
        font-family: Arial, sans-serif;
    }

    .score-interpretation {
        display: inline-block;
        margin-top: 0.55rem;
        padding: 5px 12px;
        border-radius: 999px;

        background: #29364d;
        color: #f7f2e8;

        font-size: 0.78rem;
        font-weight: 700;
    }

    /* =====================================================
       RECOMMENDATION
       ===================================================== */

    .recommendation-title {
        color: #756d61;
        font-size: 0.9rem;
        margin-bottom: 0.55rem;
        text-align: center;
        font-family: Arial, sans-serif;
    }

    .recommendation {
        padding: 0.8rem 1rem;
        border-radius: 9px;
        font-weight: 800;
        text-align: center;
        font-family: Arial, sans-serif;
    }

    .shortlist {
        background: #dfeada;
        color: #315f3c;
        border: 1px solid #b9cfb4;
    }

    .review {
        background: #f3e7c7;
        color: #80611e;
        border: 1px solid #d8c28c;
    }

    .reject {
        background: #f0dada;
        color: #7d3030;
        border: 1px solid #d5abab;
    }

    /* =====================================================
       SKILLS
       ===================================================== */

    .skill-container {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 0.4rem;
    }

    .skill-tag {
        background: #e9eef3;
        color: #29364d;

        border: 1px solid #b9c6d5;

        border-radius: 7px;

        padding: 5px 10px;

        font-size: 0.78rem;
        font-family: Arial, sans-serif;
        font-weight: 700;
    }

    .missing-tag {
        background: #f4e2df;
        color: #873e42;

        border: 1px solid #d8b4af;

        border-radius: 7px;

        padding: 5px 10px;

        font-size: 0.78rem;
        font-family: Arial, sans-serif;
        font-weight: 700;
    }

    /* =====================================================
       AI ANALYSIS
       ===================================================== */

    .analysis-card {
        background:
            linear-gradient(
                135deg,
                #29364d 0%,
                #35445f 100%
            );

        color: #f7f2e8;

        border: 1px solid #a88a59;

        border-radius: 14px;

        padding: 1.35rem 1.45rem;

        margin-top: 0.7rem;
        margin-bottom: 0.75rem;

        box-shadow:
            0 8px 22px rgba(41, 54, 77, 0.18);
    }

    .analysis-title {
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 0.65rem;
    }

    .analysis-text {
        color: #eee4d2;
        font-family: Arial, sans-serif;
        font-size: 0.94rem;
        line-height: 1.65;
    }

    /* =====================================================
       SCORE GUIDE
       ===================================================== */

    .score-guide {
        background: #fbf8f1;
        border: 1px solid #d8c7a8;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-top: 0.7rem;
        margin-bottom: 0.75rem;
    }

    .score-guide-title {
        color: #29364d;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .score-guide-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        border-bottom: 1px solid #eadfce;
        font-family: Arial, sans-serif;
        font-size: 0.82rem;
    }

    .score-guide-row:last-child {
        border-bottom: none;
    }

    /* =====================================================
       STREAMLIT ELEMENTS
       ===================================================== */

    .stButton > button {
        background: #29364d;
        color: #f7f2e8;

        border: 1px solid #29364d;
        border-radius: 8px;

        min-height: 40px;

        font-family: Arial, sans-serif;
        font-weight: 700;
    }

    .stButton > button:hover {
        background: #35445f;
        color: white;
        border-color: #35445f;
    }

    [data-testid="stFileUploader"] {
        background: #f2eee6;
        border: 1px dashed #bba77e;
        border-radius: 10px;
        padding: 0.5rem;
    }

    textarea,
    input {
        border-radius: 8px !important;
    }

    div[data-testid="stMetric"] {
        background: #fbf8f1;
        border: 1px solid #d8c7a8;
        border-radius: 10px;
        padding: 0.65rem;
    }

    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;
        color: #81796c;
        padding: 1.2rem 0 0.5rem;
        font-family: Arial, sans-serif;
        font-size: 0.75rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "resume_id" not in st.session_state:
    st.session_state.resume_id = None

if "profile" not in st.session_state:
    st.session_state.profile = None

if "job_id" not in st.session_state:
    st.session_state.job_id = None

if "job_title" not in st.session_state:
    st.session_state.job_title = ""

if "evaluation" not in st.session_state:
    st.session_state.evaluation = None

if "shortlist" not in st.session_state:
    st.session_state.shortlist = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def api_error(response, default_message):
    """Safely extract an API error."""

    try:
        data = response.json()

        if isinstance(data, dict):
            return data.get(
                "detail",
                default_message
            )

        return default_message

    except Exception:
        return default_message


def normalize_skill(value):
    """
    Normalize skill text for comparison.
    """

    value = str(value).lower().strip()

    value = value.replace(
        " (explicit)",
        ""
    )

    value = value.replace(
        " (explicit framework)",
        ""
    )

    value = re.sub(
        r"[^a-z0-9+#.\-/ ]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def make_skill_tags(
    skills,
    missing=False
):
    """
    Create skill badges.
    """

    if not skills:
        return (
            "<span style="
            "'color:#81796c;font-family:Arial;'>"
            "None identified"
            "</span>"
        )

    css_class = (
        "missing-tag"
        if missing
        else "skill-tag"
    )

    tags = []

    for skill in skills:

        safe_skill = html.escape(
            str(skill)
        )

        tags.append(
            f"""
            <span class="{css_class}">
                {safe_skill}
            </span>
            """
        )

    return (
        "<div class='skill-container'>"
        + "".join(tags)
        + "</div>"
    )


def recommendation_class(
    recommendation
):
    """
    CSS class for recommendation.
    """

    recommendation = str(
        recommendation
    ).lower()

    if recommendation == "shortlist":
        return "shortlist"

    if recommendation == "review":
        return "review"

    return "reject"


def score_interpretation(score):
    """
    Convert score into a human-readable interpretation.
    """

    if score >= 8:
        return "Excellent Match"

    if score >= 7:
        return "Strong Match"

    if score >= 5:
        return "Review"

    return "Weak Match"


def clean_skill_gaps(
    missing_skills,
    profile
):
    """
    Prevent skills from being shown as missing
    when they are already demonstrated somewhere
    in the candidate profile.

    Evidence is checked against:
        - extracted skills
        - experience
        - projects
        - education
    """

    if not missing_skills:
        return []

    profile = profile or {}

    evidence_parts = []

    profile_skills = profile.get(
        "skills",
        []
    )

    experience = profile.get(
        "experience",
        []
    )

    education = profile.get(
        "education",
        []
    )

    projects = profile.get(
        "projects",
        []
    )

    evidence_parts.extend(
        str(item)
        for item in profile_skills
    )

    evidence_parts.extend(
        str(item)
        for item in experience
    )

    evidence_parts.extend(
        str(item)
        for item in projects
    )

    evidence_parts.extend(
        str(item)
        for item in education
    )

    evidence_text = normalize_skill(
        " ".join(evidence_parts)
    )

    cleaned = []

    for skill in missing_skills:

        normalized = normalize_skill(
            skill
        )

        if not normalized:
            continue

        # Direct evidence
        if normalized in evidence_text:
            continue

        # Common aliases
        aliases = {
            "ml": [
                "machine learning"
            ],
            "machine learning": [
                "ml"
            ],
            "genai": [
                "generative ai"
            ],
            "generative ai": [
                "genai"
            ],
            "llm": [
                "large language model",
                "large language models",
                "llms"
            ],
            "llms": [
                "large language model",
                "large language models",
                "llm"
            ],
            "nlp": [
                "natural language processing"
            ],
            "natural language processing": [
                "nlp"
            ],
            "tensorflow": [
                "tensorflow"
            ],
            "deep learning": [
                "deep learning"
            ],
        }

        found = False

        for alias in aliases.get(
            normalized,
            []
        ):

            if normalize_skill(
                alias
            ) in evidence_text:

                found = True
                break

        if not found:
            cleaned.append(skill)

    return cleaned


def check_backend():
    """
    Check whether FastAPI backend is online.
    """

    try:

        response = requests.get(
            f"{API_URL}/",
            timeout=3
        )

        return response.status_code < 500

    except requests.RequestException:
        return False


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            📄 Resume Screener
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-label">
            System Status
        </div>
        """,
        unsafe_allow_html=True
    )

    if check_backend():

        st.success(
            "Backend Online"
        )

    else:

        st.error(
            "Backend Offline"
        )

    st.divider()

    st.markdown(
        """
        <div class="sidebar-label">
            Current Session
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.resume_id:

        st.markdown(
            f"""
            <div class="sidebar-value">
                Resume ID:
                <strong>
                    {st.session_state.resume_id}
                </strong>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.caption(
            "Resume: Not uploaded"
        )

    if st.session_state.job_id:

        st.markdown(
            f"""
            <div class="sidebar-value">
                Job ID:
                <strong>
                    {st.session_state.job_id}
                </strong>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.caption(
            "Job: Not created"
        )

    st.divider()

    if st.button(
        "🔄 Reset Session",
        use_container_width=True
    ):

        st.session_state.resume_id = None
        st.session_state.profile = None
        st.session_state.job_id = None
        st.session_state.job_title = ""
        st.session_state.evaluation = None
        st.session_state.shortlist = None

        st.rerun()


# =========================================================
# HERO
# =========================================================

st.html(
    """
    <div class="hero">

        <div class="hero-title">
            📄 Smart Resume Screener
        </div>

        <div class="hero-subtitle">
            AI-powered recruitment intelligence for
            resume parsing, candidate-job matching,
            skill-gap analysis, and intelligent
            shortlisting.
        </div>

        <div class="hero-pills">

            <span class="hero-pill">
                AI Resume Parsing
            </span>

            <span class="hero-pill">
                Candidate Matching
            </span>

            <span class="hero-pill">
                Skill Gap Analysis
            </span>

            <span class="hero-pill">
                Smart Shortlisting
            </span>

        </div>

    </div>
    """
)


# =========================================================
# SESSION OVERVIEW
# =========================================================

resume_ready = bool(
    st.session_state.resume_id
)

job_ready = bool(
    st.session_state.job_id
)

evaluation_ready = bool(
    st.session_state.evaluation
)

overview1, overview2, overview3 = st.columns(
    3,
    gap="medium"
)

with overview1:

    st.metric(
        "Resume",
        "Ready"
        if resume_ready
        else "Pending"
    )

with overview2:

    st.metric(
        "Job",
        "Ready"
        if job_ready
        else "Pending"
    )

with overview3:

    if evaluation_ready:

        latest_score = float(
            st.session_state.evaluation.get(
                "match_score",
                0
            )
        )

        st.metric(
            "Latest Match",
            f"{latest_score:.1f}/10"
        )

    else:

        st.metric(
            "Latest Match",
            "—"
        )


# =========================================================
# 1. UPLOAD RESUME
# =========================================================

st.markdown(
    """
    <div class="section-title">
        1. Upload Resume
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-description">
        Upload a candidate resume in PDF or TXT format.
        The AI will extract structured candidate information.
    </div>
    """,
    unsafe_allow_html=True
)


upload_col, profile_col = st.columns(
    [1, 1.45],
    gap="medium"
)


# =========================================================
# RESUME UPLOAD
# =========================================================

with upload_col:

    resume_file = st.file_uploader(
        "Choose Resume",
        type=[
            "pdf",
            "txt"
        ],
        help="Supported formats: PDF and TXT"
    )

    if resume_file:

        st.info(
            f"Selected: **{resume_file.name}**"
        )

        if st.button(
            "🔍 Parse Resume",
            use_container_width=True
        ):

            with st.spinner(
                "Analyzing resume..."
            ):

                try:

                    files = {
                        "file": (
                            resume_file.name,
                            resume_file.getvalue()
                        )
                    }

                    response = requests.post(
                        f"{API_URL}/resumes/upload",
                        files=files,
                        timeout=120
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.session_state.resume_id = data[
                            "resume_id"
                        ]

                        st.session_state.profile = data[
                            "profile"
                        ]

                        st.session_state.evaluation = None

                        st.success(
                            "Resume parsed successfully."
                        )

                    else:

                        st.error(
                            api_error(
                                response,
                                "Failed to parse resume."
                            )
                        )

                except requests.RequestException as e:

                    st.error(
                        f"Backend connection failed: {e}"
                    )


# =========================================================
# CANDIDATE PROFILE
# =========================================================

with profile_col:

    profile = st.session_state.profile

    if profile:

        name = profile.get(
            "name",
            "Unknown"
        )

        email = profile.get(
            "email",
            "Not available"
        )

        phone = profile.get(
            "phone",
            "Not available"
        )

        skills = profile.get(
            "skills",
            []
        )

        safe_name = html.escape(
            str(name)
        )

        safe_email = html.escape(
            str(email)
        )

        safe_phone = html.escape(
            str(phone)
        )

        # IMPORTANT:
        # One complete HTML block.
        # This prevents raw <div> text appearing.

        st.html(
            f"""
            <div class="card">

                <div class="card-title">
                    👤 Candidate Profile
                </div>

                <div class="profile-info">

                    <div>
                        <strong>Name:</strong>
                        {safe_name}
                    </div>

                    <div>
                        <strong>Email:</strong>
                        {safe_email}
                    </div>

                    <div>
                        <strong>Phone:</strong>
                        {safe_phone}
                    </div>

                    <div style="
                        margin-top:0.55rem;
                        font-weight:800;
                        color:#29364d;
                    ">
                        Skills
                    </div>

                </div>

                {make_skill_tags(skills)}

            </div>
            """
        )


# =========================================================
# EXPERIENCE + EDUCATION
# =========================================================

if st.session_state.profile:

    profile = st.session_state.profile

    exp_col, edu_col = st.columns(
        2,
        gap="medium"
    )


    # -----------------------------------------------------
    # EXPERIENCE
    # -----------------------------------------------------

    with exp_col:

        experience = profile.get(
            "experience",
            []
        )

        experience_html = ""

        if experience:

            for item in experience:

                safe_item = html.escape(
                    str(item)
                )

                experience_html += (
                    f"""
                    <div style="
                        margin-bottom:0.5rem;
                        line-height:1.5;
                        font-family:Arial,sans-serif;
                        font-size:0.88rem;
                        color:#4f4a43;
                    ">
                        • {safe_item}
                    </div>
                    """
                )

        else:

            experience_html = (
                """
                <div style="
                    color:#81796c;
                    font-family:Arial,sans-serif;
                ">
                    No experience information extracted.
                </div>
                """
            )

        st.html(
            f"""
            <div class="card">

                <div class="card-title">
                    💼 Experience & Projects
                </div>

                {experience_html}

            </div>
            """
        )


    # -----------------------------------------------------
    # EDUCATION
    # -----------------------------------------------------

    with edu_col:

        education = profile.get(
            "education",
            []
        )

        education_html = ""

        if education:

            for item in education:

                safe_item = html.escape(
                    str(item)
                )

                education_html += (
                    f"""
                    <div style="
                        margin-bottom:0.5rem;
                        line-height:1.5;
                        font-family:Arial,sans-serif;
                        font-size:0.88rem;
                        color:#4f4a43;
                    ">
                        • {safe_item}
                    </div>
                    """
                )

        else:

            education_html = (
                """
                <div style="
                    color:#81796c;
                    font-family:Arial,sans-serif;
                ">
                    No education information extracted.
                </div>
                """
            )

        st.html(
            f"""
            <div class="card">

                <div class="card-title">
                    🎓 Education
                </div>

                {education_html}

            </div>
            """
        )


# =========================================================
# 2. JOB DESCRIPTION
# =========================================================

st.markdown(
    """
    <div class="section-title">
        2. Job Description
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-description">
        Enter the role and paste the job requirements.
        The system will compare them against the candidate profile.
    </div>
    """,
    unsafe_allow_html=True
)


job_title = st.text_input(
    "Job Title",
    value=st.session_state.job_title,
    placeholder="e.g. AI/ML Engineer"
)


job_text = st.text_area(
    "Job Description",
    height=180,
    placeholder=(
        "Paste the complete job description here..."
    )
)


if st.session_state.job_id:

    st.info(
        f"Current Job ID: "
        f"{st.session_state.job_id}"
    )


if st.button(
    "💾 Save Job Description",
    use_container_width=True
):

    if not job_title.strip():

        st.warning(
            "Please enter a job title."
        )

    elif not job_text.strip():

        st.warning(
            "Please enter a job description."
        )

    else:

        with st.spinner(
            "Saving job description..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/jobs",
                    json={
                        "title": job_title,
                        "description_text": job_text
                    },
                    timeout=30
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.job_id = data[
                        "job_id"
                    ]

                    st.session_state.job_title = job_title

                    st.session_state.evaluation = None

                    st.success(
                        f"Job saved successfully. "
                        f"Job ID: {data['job_id']}"
                    )

                else:

                    st.error(
                        api_error(
                            response,
                            "Failed to save job."
                        )
                    )

            except requests.RequestException as e:

                st.error(
                    f"Backend connection failed: {e}"
                )


# =========================================================
# 3. EVALUATE CANDIDATE
# =========================================================

st.markdown(
    """
    <div class="section-title">
        3. Evaluate Candidate
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-description">
        Run the candidate-job matching engine to calculate
        the fit score, identify skill gaps, and generate
        an AI recommendation.
    </div>
    """,
    unsafe_allow_html=True
)


if st.button(
    "🎯 Evaluate Candidate",
    use_container_width=True
):

    resume_id = st.session_state.resume_id
    job_id = st.session_state.job_id

    if not resume_id:

        st.warning(
            "Please upload and parse a resume first."
        )

    elif not job_id:

        st.warning(
            "Please save a job description first."
        )

    else:

        with st.spinner(
            "Evaluating candidate against the job..."
        ):

            try:

                response = requests.post(
                    f"{API_URL}/match",
                    params={
                        "resume_id": resume_id,
                        "job_id": job_id
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state.evaluation = result

                else:

                    st.error(
                        api_error(
                            response,
                            "Failed to evaluate candidate."
                        )
                    )

            except requests.RequestException as e:

                st.error(
                    f"Backend connection failed: {e}"
                )


# =========================================================
# DISPLAY EVALUATION
# =========================================================

result = st.session_state.evaluation


if result:

    score = float(
        result.get(
            "match_score",
            0
        )
    )

    recommendation = result.get(
        "recommendation",
        "Review"
    )

    candidate_name = result.get(
        "candidate_name",
        "Candidate"
    )

    matching_skills = result.get(
        "matching_skills",
        []
    )

    missing_skills = result.get(
        "missing_skills",
        []
    )

    justification = result.get(
        "justification",
        "No justification provided."
    )

    # -----------------------------------------------------
    # CLEAN SKILL GAPS
    # -----------------------------------------------------

    missing_skills = clean_skill_gaps(
        missing_skills,
        st.session_state.profile
    )

    # -----------------------------------------------------
    # SCORE INTERPRETATION
    # -----------------------------------------------------

    interpretation = score_interpretation(
        score
    )

    st.markdown(
        """
        <div class="section-title">
            📊 AI Evaluation Result
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        f"Candidate: {candidate_name}"
    )


    # -----------------------------------------------------
    # SCORE + RECOMMENDATION
    # -----------------------------------------------------

    score_col, recommendation_col = st.columns(
        2,
        gap="medium"
    )


    with score_col:

        st.html(
            f"""
            <div class="score-card">

                <div class="score-number">
                    {score:.1f}/10
                </div>

                <div class="score-label">
                    Candidate Match Score
                </div>

                <div class="score-interpretation">
                    {interpretation}
                </div>

            </div>
            """
        )

        st.progress(
            min(
                max(
                    score / 10,
                    0
                ),
                1
            )
        )


    with recommendation_col:

        css_class = recommendation_class(
            recommendation
        )

        safe_recommendation = html.escape(
            str(recommendation)
        )

        st.html(
            f"""
            <div class="score-card">

                <div class="recommendation-title">
                    AI Recommendation
                </div>

                <div class="recommendation {css_class}">
                    {safe_recommendation}
                </div>

            </div>
            """
        )


    # -----------------------------------------------------
    # SCORE GUIDE
    # -----------------------------------------------------

    st.html(
        """
        <div class="score-guide">

            <div class="score-guide-title">
                Score Interpretation
            </div>

            <div class="score-guide-row">
                <span>8.0 – 10.0</span>
                <strong>Excellent Match</strong>
            </div>

            <div class="score-guide-row">
                <span>7.0 – 7.9</span>
                <strong>Strong Match</strong>
            </div>

            <div class="score-guide-row">
                <span>5.0 – 6.9</span>
                <strong>Review</strong>
            </div>

            <div class="score-guide-row">
                <span>Below 5.0</span>
                <strong>Weak Match</strong>
            </div>

        </div>
        """
    )


    # -----------------------------------------------------
    # SKILL ANALYSIS
    # -----------------------------------------------------

    match_col, missing_col = st.columns(
        2,
        gap="medium"
    )


    with match_col:

        st.html(
            f"""
            <div class="card">

                <div class="card-title">
                    ✅ Matching Skills
                </div>

                {make_skill_tags(
                    matching_skills
                )}

            </div>
            """
        )


    with missing_col:

        st.html(
            f"""
            <div class="card">

                <div class="card-title">
                    ⚠️ Skill Gaps
                </div>

                {make_skill_tags(
                    missing_skills,
                    missing=True
                )}

            </div>
            """
        )


    # -----------------------------------------------------
    # AI ANALYSIS
    # -----------------------------------------------------

    safe_justification = html.escape(
        str(justification)
    )

    st.html(
        f"""
        <div class="analysis-card">

            <div class="analysis-title">
                🧠 AI Analysis
            </div>

            <div class="analysis-text">
                {safe_justification}
            </div>

        </div>
        """
    )


# =========================================================
# 4. SHORTLIST
# =========================================================

st.markdown(
    """
    <div class="section-title">
        4. Shortlist Candidates
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-description">
        View candidates ranked by their match score
        for a selected job.
    </div>
    """,
    unsafe_allow_html=True
)


default_job_id = (
    st.session_state.job_id
    if st.session_state.job_id
    else 1
)


job_id_lookup = st.number_input(
    "Job ID",
    min_value=1,
    value=int(default_job_id),
    step=1
)


if st.button(
    "🏆 Show Shortlist",
    use_container_width=True
):

    with st.spinner(
        "Loading ranked candidates..."
    ):

        try:

            response = requests.get(
                f"{API_URL}/candidates/"
                f"{int(job_id_lookup)}",
                timeout=30
            )

            if response.status_code == 200:

                st.session_state.shortlist = (
                    response.json()
                )

            else:

                st.error(
                    api_error(
                        response,
                        "Failed to fetch candidates."
                    )
                )

        except requests.RequestException as e:

            st.error(
                f"Backend connection failed: {e}"
            )


# =========================================================
# DISPLAY SHORTLIST
# =========================================================

candidates = st.session_state.shortlist


if candidates is not None:

    if not candidates:

        st.info(
            "No candidates have been evaluated "
            "for this job yet."
        )

    else:

        st.markdown(
            "### 🏆 Ranked Candidates"
        )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        total_candidates = len(
            candidates
        )

        shortlisted = sum(
            1
            for c in candidates
            if c.get(
                "recommendation"
            ) == "Shortlist"
        )

        review_count = sum(
            1
            for c in candidates
            if c.get(
                "recommendation"
            ) == "Review"
        )

        rejected = sum(
            1
            for c in candidates
            if c.get(
                "recommendation"
            ) == "Reject"
        )


        metric1, metric2, metric3, metric4 = (
            st.columns(4)
        )


        with metric1:

            st.metric(
                "Candidates",
                total_candidates
            )


        with metric2:

            st.metric(
                "Shortlisted",
                shortlisted
            )


        with metric3:

            st.metric(
                "Review",
                review_count
            )


        with metric4:

            st.metric(
                "Rejected",
                rejected
            )


        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        table_data = []

        for index, candidate in enumerate(
            candidates,
            start=1
        ):

            table_data.append(
                {
                    "Rank": index,

                    "Candidate": (
                        candidate.get(
                            "candidate_name"
                        )
                        or "Unknown"
                    ),

                    "Score": float(
                        candidate.get(
                            "match_score",
                            0
                        )
                    ),

                    "Recommendation": candidate.get(
                        "recommendation",
                        "Review"
                    ),
                }
            )


        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True,

            column_config={

                "Rank":
                    st.column_config.NumberColumn(
                        "Rank",
                        width="small"
                    ),

                "Candidate":
                    st.column_config.TextColumn(
                        "Candidate",
                        width="large"
                    ),

                "Score":
                    st.column_config.NumberColumn(
                        "Score",
                        format="%.1f / 10"
                    ),

                "Recommendation":
                    st.column_config.TextColumn(
                        "Recommendation"
                    ),
            }
        )


        # -------------------------------------------------
        # DETAILS
        # -------------------------------------------------

        st.markdown(
            "### Candidate Details"
        )


        for index, candidate in enumerate(
            candidates,
            start=1
        ):

            name = candidate.get(
                "candidate_name",
                "Unknown"
            )

            score = float(
                candidate.get(
                    "match_score",
                    0
                )
            )

            recommendation = candidate.get(
                "recommendation",
                "Review"
            )

            with st.expander(
                f"#{index}  "
                f"{name}  —  "
                f"{score:.1f}/10  —  "
                f"{recommendation}"
            ):

                detail_col1, detail_col2 = (
                    st.columns(2)
                )


                with detail_col1:

                    st.markdown(
                        "**Matching Skills**"
                    )

                    st.html(
                        make_skill_tags(
                            candidate.get(
                                "matching_skills",
                                []
                            )
                        )
                    )


                with detail_col2:

                    st.markdown(
                        "**Missing Skills**"
                    )

                    cleaned_missing = (
                        clean_skill_gaps(
                            candidate.get(
                                "missing_skills",
                                []
                            ),
                            st.session_state.profile
                        )
                    )

                    st.html(
                        make_skill_tags(
                            cleaned_missing,
                            missing=True
                        )
                    )


                st.markdown(
                    "**AI Justification**"
                )

                st.info(
                    candidate.get(
                        "justification",
                        "No justification available."
                    )
                )


# =========================================================
# FOOTER
# =========================================================

st.html(
    """
    <div class="footer">
        Smart Resume Screener
        · FastAPI
        · Streamlit
        · Groq
        · SQLite
    </div>
    """
)