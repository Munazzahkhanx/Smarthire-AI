
import streamlit as st
import pandas as pd
import plotly.express as px
from pypdf import PdfReader
from datetime import date
import re

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="SmartHire AI | Talent Acquisition",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. PROFESSIONAL DESIGN / CSS
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #F5F7FB;
}

[data-testid="stSidebar"] {
    background-color: #172B4D;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 8px;
    border-radius: 7px;
}

h1, h2, h3 {
    color: #172B4D;
    font-weight: 700;
}

p {
    color: #526179;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E5EAF2;
    padding: 20px;
    border-radius: 12px;
}

[data-testid="stMetricValue"] {
    color: #172B4D;
    font-weight: 700;
}

.stButton button {
    background-color: #315EF4;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    padding: 9px 18px;
}

.stButton button:hover {
    background-color: #2449CB;
    color: white;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 8px;
}

[data-testid="stDataFrame"] {
    border-radius: 10px;
}

hr {
    border-color: #E5EAF2;
}

.brand-box {
    background: #223B64;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 22px;
}

.brand-name {
    color: white;
    font-size: 22px;
    font-weight: 800;
}

.brand-subtitle {
    color: #B9C8DF;
    font-size: 11px;
}

.section-label {
    color: #77869B;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.info-card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #E5EAF2;
}

.chat-header {
    background: #172B4D;
    color: white;
    padding: 18px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. INITIAL DATA
# ==========================================

if "candidates" not in st.session_state:
    st.session_state.candidates = [
        {
            "Name": "Rahul Sharma",
            "Email": "rahul@gmail.com",
            "Skills": "Python, SQL, Machine Learning",
            "Experience": 2,
            "Score": 90,
            "Status": "Shortlisted",
            "Interview": "Scheduled",
            "Job": "Python Developer"
        },
        {
            "Name": "Priya Reddy",
            "Email": "priya@gmail.com",
            "Skills": "Java, SQL, HTML",
            "Experience": 1,
            "Score": 65,
            "Status": "Under Review",
            "Interview": "Not Scheduled",
            "Job": "Software Developer"
        },
        {
            "Name": "Arjun Kumar",
            "Email": "arjun@gmail.com",
            "Skills": "Python, Java, SQL",
            "Experience": 3,
            "Score": 95,
            "Status": "Shortlisted",
            "Interview": "Completed",
            "Job": "Python Developer"
        }
    ]

if "jobs" not in st.session_state:
    st.session_state.jobs = [
        {
            "Job Title": "Python Developer",
            "Required Skills": "Python, SQL, Machine Learning"
        },
        {
            "Job Title": "Software Developer",
            "Required Skills": "Java, SQL, HTML"
        },
        {
            "Job Title": "Data Analyst",
            "Required Skills": "Python, Excel, SQL"
        }
    ]

if "interview_dates" not in st.session_state:
    st.session_state.interview_dates = {}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_candidate" not in st.session_state:
    st.session_state.pending_candidate = None


# ==========================================
# 4. RESUME SCORING
# ==========================================

def calculate_score(resume, required_skills, experience):

    resume = resume.lower()

    matched = []

    for skill in required_skills:

        if skill.lower() in resume:
            matched.append(skill)

    if len(required_skills) > 0:
        skill_score = (
            len(matched) / len(required_skills)
        ) * 80
    else:
        skill_score = 0

    experience_score = min(experience * 4, 20)

    total_score = round(
        skill_score + experience_score
    )

    return total_score, matched


# ==========================================
# 5. PDF / TEXT EXTRACTION
# ==========================================

def extract_resume(file):

    if file.name.lower().endswith(".pdf"):

        reader = PdfReader(file)

        resume_text = ""

        for page in reader.pages:
            resume_text += page.extract_text() or ""

        return resume_text

    return file.read().decode(
        "utf-8", errors="ignore"
    )


# ==========================================
# 6. SMART HR ASSISTANT ENGINE
# ==========================================

def hr_assistant(query):

    q = query.lower()

    candidates = st.session_state.candidates
    jobs = st.session_state.jobs

    data = pd.DataFrame(candidates)

    # Recruitment overview

    if any(word in q for word in [
        "how many", "total candidates",
        "candidate count", "recruitment summary",
        "overview", "statistics"
    ]):

        total = len(candidates)

        shortlisted = sum(
            c["Status"] == "Shortlisted"
            for c in candidates
        )

        rejected = sum(
            c["Status"] == "Rejected"
            for c in candidates
        )

        review = sum(
            c["Status"] == "Under Review"
            for c in candidates
        )

        return f"""
        **Recruitment Summary**

        - Total candidates: {total}
        - Shortlisted: {shortlisted}
        - Under review: {review}
        - Rejected: {rejected}

        There are currently {len(jobs)} job positions
        in the recruitment system.
        """

    # Top candidates

    if any(word in q for word in [
        "best candidate", "top candidate",
        "highest score", "recommend",
        "best candidates", "top candidates"
    ]):

        if not candidates:
            return "There are no candidates available yet."

        top = sorted(
            candidates,
            key=lambda c: c["Score"],
            reverse=True
        )[:3]

        answer = "**Top Candidate Recommendations**\n\n"

        for c in top:

            answer += (
                f"- **{c['Name']}** — "
                f"{c['Score']}/100, "
                f"{c['Job']}, "
                f"{c['Status']}\n"
            )

        answer += (
            "\nThese are score-based recommendations. "
            "Please review resumes and interview candidates "
            "before making hiring decisions."
        )

        return answer

    # Interview questions

    if any(word in q for word in [
        "interview", "scheduled",
        "upcoming", "interviews"
    ]):

        scheduled = [
            c for c in candidates
            if c["Interview"] == "Scheduled"
        ]

        if not scheduled:
            return "There are currently no scheduled interviews."

        answer = "**Scheduled Interviews**\n\n"

        for c in scheduled:

            interview_date = st.session_state.interview_dates.get(
                c["Email"], "Date not recorded"
            )

            answer += (
                f"- {c['Name']} — "
                f"{c['Job']} — {interview_date}\n"
            )

        return answer

    # Job information

    if any(word in q for word in [
        "job", "vacancy", "position", "opening", "role"
    ]):

        answer = "**Available Job Positions**\n\n"

        for job in jobs:

            answer += (
                f"- **{job['Job Title']}**\n"
                f"  Required skills: {job['Required Skills']}\n"
            )

        return answer

    # Candidate search by name

    for candidate in candidates:

        name_parts = candidate["Name"].lower().split()

        if all(
            part in q for part in name_parts
        ):

            return f"""
            **Candidate Profile**

            - Name: {candidate['Name']}
            - Email: {candidate['Email']}
            - Job: {candidate['Job']}
            - Skills: {candidate['Skills']}
            - Experience: {candidate['Experience']} years
            - Score: {candidate['Score']}/100
            - Status: {candidate['Status']}
            - Interview: {candidate['Interview']}

            **Recommendation:** Review the candidate's
            resume and interview performance before
            making a hiring decision.
            """

    # Job-specific candidate search

    matching_job = next(
        (
            j for j in jobs
            if j["Job Title"].lower() in q
        ),
        None
    )

    if matching_job:

        matching_candidates = [
            c for c in candidates
            if c["Job"] == matching_job["Job Title"]
        ]

        matching_candidates.sort(
            key=lambda c: c["Score"],
            reverse=True
        )

        if not matching_candidates:
            return "No candidates have applied for this position yet."

        answer = (
            f"**Candidates for {matching_job['Job Title']}**\n\n"
        )

        for c in matching_candidates:

            answer += (
                f"- {c['Name']} — {c['Score']}/100 "
                f"({c['Status']})\n"
            )

        return answer

    # Skill information

    if "skill" in q:

        return """
        **Skill Matching**

        SmartHire compares skills extracted from a
        candidate's resume against the skills required
        for a particular job.

        The system assigns 80 points to skill matching
        and up to 20 points to experience.
        """

    # Scoring explanation

    if any(word in q for word in [
        "score", "scoring", "calculate", "algorithm"
    ]):

        return """
        **Candidate Scoring Algorithm**

        SmartHire uses two components:

        1. Skill matching: Maximum 80 points.
        2. Experience: Maximum 20 points.

        Total score = Skill score + Experience score.

        This is a rule-based demonstration, not a
        trained machine-learning model.
        """

    # Recruitment process

    if any(word in q for word in [
        "recruitment process", "hiring process",
        "how does recruitment", "steps"
    ]):

        return """
        **Recruitment Workflow**

        1. Create a job vacancy.
        2. Receive candidate resumes.
        3. Screen resumes.
        4. Match skills with job requirements.
        5. Review candidate scores.
        6. Shortlist suitable candidates.
        7. Schedule interviews.
        8. Complete the hiring process.
        """

    # Greeting

    if any(word in q for word in [
        "hello", "hi", "hey", "good morning"
    ]):

        return """
        Hello! Welcome to SmartHire AI.

        I can help you with:

        - Candidate recommendations
        - Candidate profiles
        - Recruitment statistics
        - Job vacancies
        - Interview schedules
        - Resume scoring
        - HR and recruitment questions

        What would you like to know?
        """

    return """
    I can help you manage recruitment information.

    Try asking me questions such as:

    - Who are the top candidates?
    - How many candidates are shortlisted?
    - Show Python Developer candidates.
    - What interviews are scheduled?
    - Explain the candidate scoring algorithm.
    - What job vacancies are available?
    - Tell me about Rahul Sharma.

    You can also ask general recruitment questions.
    """


# ==========================================
# 7. SIDEBAR NAVIGATION
# ==========================================

st.sidebar.markdown("""
<div class="brand-box">
    <div class="brand-name">SmartHire AI</div>
    <div class="brand-subtitle">
        TALENT ACQUISITION PLATFORM
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="section-label">WORKSPACE</div>',
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Resume Screening",
        "Candidates",
        "Job Management",
        "Interview Management",
        "Hiring Analytics",
        "HR Assistant"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

st.sidebar.caption("SYSTEM INFORMATION")

st.sidebar.write("Version 2.0")
st.sidebar.write("Recruitment Management")

st.sidebar.markdown("---")

st.sidebar.caption(
    "SmartHire AI | 2026"
)


# ==========================================
# 8. DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("Recruitment Overview")

    st.caption(
        "Monitor your hiring pipeline and recruitment performance."
    )

    data = pd.DataFrame(
        st.session_state.candidates
    )

    total = len(data)

    shortlisted = sum(
        c["Status"] == "Shortlisted"
        for c in st.session_state.candidates
    )

    under_review = sum(
        c["Status"] == "Under Review"
        for c in st.session_state.candidates
    )

    interviews = sum(
        c["Interview"] == "Scheduled"
        for c in st.session_state.candidates
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Candidates", total)

    c2.metric("Shortlisted", shortlisted)

    c3.metric("Under Review", under_review)

    c4.metric("Interviews Scheduled", interviews)

    st.markdown("---")

    left, right = st.columns([1.3, 1])

    with left:

        st.subheader("Candidate Overview")

        if total > 0:

            chart = px.pie(
                data,
                names="Status",
                hole=0.65,
                color_discrete_sequence=[
                    "#315EF4",
                    "#16A6A0",
                    "#F0A44B"
                ]
            )

            chart.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font_color="#172B4D",
                margin=dict(t=20, b=20, l=20, r=20)
            )

            st.plotly_chart(
                chart,
                use_container_width=True
            )

    with right:

        st.subheader("Hiring Snapshot")

        st.markdown(
            '<div class="info-card">',
            unsafe_allow_html=True
        )

        st.write("**Open Job Positions**")
        st.title(len(st.session_state.jobs))

        st.write("**Average Candidate Score**")

        if total > 0:
            st.title(
                str(round(data["Score"].mean(), 1)) + "/100"
            )
        else:
            st.title("0/100")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Recent Applicants")

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 9. RESUME SCREENING
# ==========================================

elif page == "Resume Screening":

    st.title("Resume Screening")

    st.caption(
        "Upload resumes and evaluate candidates against job requirements."
    )

    with st.container(border=True):

        st.subheader("Candidate Information")

        with st.form("resume_form"):

            name = st.text_input("Full Name")

            email = st.text_input("Email Address")

            experience = st.number_input(
                "Years of Experience",
                min_value=0,
                max_value=30,
                value=1
            )

            job_names = [
                j["Job Title"]
                for j in st.session_state.jobs
            ]

            selected_job = st.selectbox(
                "Select Job Position",
                job_names
            )

            uploaded_file = st.file_uploader(
                "Upload Candidate Resume",
                type=["pdf", "txt"]
            )

            submit = st.form_submit_button(
                "Analyze Resume"
            )

    if submit:

        if not name or not email or not uploaded_file:

            st.error(
                "Please complete all fields and upload a resume."
            )

        else:

            resume_text = extract_resume(uploaded_file)

            if not resume_text.strip():

                st.error(
                    "Unable to extract text. Please upload a text-based PDF or TXT file."
                )

            else:

                job = next(
                    j for j in st.session_state.jobs
                    if j["Job Title"] == selected_job
                )

                skills = [
                    s.strip()
                    for s in job["Required Skills"].split(",")
                    if s.strip()
                ]

                score, matched = calculate_score(
                    resume_text,
                    skills,
                    experience
                )

                if score >= 70:
                    status = "Shortlisted"
                elif score >= 40:
                    status = "Under Review"
                else:
                    status = "Rejected"

                st.session_state.pending_candidate = {
                    "Name": name,
                    "Email": email,
                    "Skills": ", ".join(matched),
                    "Experience": experience,
                    "Score": score,
                    "Status": status,
                    "Interview": "Not Scheduled",
                    "Job": selected_job
                }

    if st.session_state.pending_candidate:

        candidate = st.session_state.pending_candidate

        st.markdown("---")

        st.subheader("Screening Results")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Candidate Score",
            str(candidate["Score"]) + "/100"
        )

        c2.metric(
            "Matched Skills",
            len(candidate["Skills"].split(","))
            if candidate["Skills"] else 0
        )

        c3.metric(
            "Experience",
            str(candidate["Experience"]) + " years"
        )

        st.write("**Matched Skills:**", candidate["Skills"])

        st.write("**Position:**", candidate["Job"])

        st.write("**Recommendation:**", candidate["Status"])

        st.caption(
            "Automated score is a preliminary aid, not a final hiring decision."
        )

        if st.button("Save Candidate"):

            exists = any(
                c["Email"].lower() == candidate["Email"].lower()
                for c in st.session_state.candidates
            )

            if exists:

                st.warning("Candidate already exists.")

            else:

                st.session_state.candidates.append(
                    candidate.copy()
                )

                st.session_state.pending_candidate = None

                st.success("Candidate saved successfully!")

                st.rerun()


# ==========================================
# 10. CANDIDATE MANAGEMENT
# ==========================================

elif page == "Candidates":

    st.title("Candidate Management")

    st.caption(
        "Search, review and manage your candidate database."
    )

    data = pd.DataFrame(
        st.session_state.candidates
    )

    if len(data) > 0:

        search = st.text_input(
            "Search candidates by name or email"
        )

        if search:

            data = data[
                data["Name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                data["Email"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        st.subheader("Update Candidate")

        candidate_options = {
            c["Name"] + " | " + c["Email"]: c["Email"]
            for c in st.session_state.candidates
        }

        selected = st.selectbox(
            "Select Candidate",
            list(candidate_options.keys())
        )

        selected_email = candidate_options[selected]

        new_status = st.selectbox(
            "Recruitment Status",
            [
                "Under Review",
                "Shortlisted",
                "Rejected"
            ]
        )

        if st.button("Update Candidate Status"):

            for c in st.session_state.candidates:

                if c["Email"] == selected_email:
                    c["Status"] = new_status

            st.success("Candidate updated successfully!")

            st.rerun()

        st.markdown("---")

        csv = pd.DataFrame(
            st.session_state.candidates
        ).to_csv(index=False).encode("utf-8")

        st.download_button(
            "Export Candidate Data",
            csv,
            "SmartHire_Candidates.csv",
            "text/csv"
        )

    else:

        st.info("No candidate records available.")


# ==========================================
# 11. JOB MANAGEMENT
# ==========================================

elif page == "Job Management":

    st.title("Job Management")

    st.caption(
        "Create and manage recruitment requirements."
    )

    with st.container(border=True):

        st.subheader("Create New Job")

        with st.form("job_form"):

            title = st.text_input("Job Title")

            skills = st.text_input(
                "Required Skills",
                placeholder="Python, SQL, Excel"
            )

            submit_job = st.form_submit_button(
                "Create Job Vacancy"
            )

        if submit_job:

            if title and skills:

                exists = any(
                    j["Job Title"].lower() == title.lower()
                    for j in st.session_state.jobs
                )

                if exists:

                    st.warning("This job already exists.")

                else:

                    st.session_state.jobs.append({
                        "Job Title": title,
                        "Required Skills": skills
                    })

                    st.success("Job created successfully!")

                    st.rerun()

            else:

                st.error("Please fill in all fields.")

    st.markdown("---")

    st.subheader("Active Job Positions")

    for job in st.session_state.jobs:

        with st.container(border=True):

            st.write("**" + job["Job Title"] + "**")

            st.caption(
                "Required Skills: " + job["Required Skills"]
            )

            applicant_count = sum(
                c["Job"] == job["Job Title"]
                for c in st.session_state.candidates
            )

            st.write(
                "Applicants: " + str(applicant_count)
            )


# ==========================================
# 12. INTERVIEW MANAGEMENT
# ==========================================

elif page == "Interview Management":

    st.title("Interview Management")

    st.caption(
        "Track interview progress and schedule candidate interviews."
    )

    candidates = st.session_state.candidates

    if candidates:

        candidate_options = {
            c["Name"] + " | " + c["Email"]: c["Email"]
            for c in candidates
        }

        selected = st.selectbox(
            "Select Candidate",
            list(candidate_options.keys())
        )

        email = candidate_options[selected]

        interview_status = st.selectbox(
            "Interview Status",
            [
                "Not Scheduled",
                "Scheduled",
                "Completed"
            ]
        )

        interview_date = st.date_input(
            "Interview Date",
            value=date.today()
        )

        if st.button("Save Interview Details"):

            for c in candidates:

                if c["Email"] == email:

                    c["Interview"] = interview_status

                    st.session_state.interview_dates[
                        email
                    ] = str(interview_date)

            st.success("Interview details saved!")

            st.rerun()

        st.markdown("---")

        st.subheader("Interview Pipeline")

        for c in candidates:

            with st.container(border=True):

                st.write("**" + c["Name"] + "**")

                st.caption(c["Job"])

                st.write(
                    "Status: " + c["Interview"]
                )

                st.write(
                    "Date: " +
                    st.session_state.interview_dates.get(
                        c["Email"], "Not scheduled"
                    )
                )

    else:

        st.info("No candidates available.")


# ==========================================
# 13. HIRING ANALYTICS
# ==========================================

elif page == "Hiring Analytics":

    st.title("Hiring Analytics")

    st.caption(
        "Analyze recruitment performance and candidate trends."
    )

    data = pd.DataFrame(
        st.session_state.candidates
    )

    if len(data) > 0:

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Average Score",
            str(round(data["Score"].mean(), 1))
        )

        c2.metric(
            "Total Applications",
            len(data)
        )

        c3.metric(
            "Job Positions",
            len(st.session_state.jobs)
        )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Candidate Score Distribution")

            fig = px.bar(
                data,
                x="Name",
                y="Score",
                color="Status",
                color_discrete_sequence=[
                    "#315EF4",
                    "#16A6A0",
                    "#F0A44B"
                ]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            st.subheader("Experience Distribution")

            fig2 = px.histogram(
                data,
                x="Experience",
                color_discrete_sequence=["#315EF4"]
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        st.subheader("Recruitment Status Analysis")

        fig3 = px.pie(
            data,
            names="Status",
            hole=0.55
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    else:

        st.info("No data available for analytics.")


# ==========================================
# 14. SMART HR ASSISTANT
# ==========================================

elif page == "HR Assistant":

    st.title("HR Intelligence Assistant")

    st.caption(
        "Your recruitment assistant for candidate insights and HR information."
    )

    st.markdown("""
    <div class="chat-header">
        SmartHire AI Assistant
        <div style="font-size:12px;font-weight:400;color:#D4DEEF;">
            Context-aware recruitment support
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    if not st.session_state.messages:

        st.info(
            "Welcome! Ask me about candidates, jobs, "
            "interviews, recruitment statistics or HR processes."
        )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask SmartHire about recruitment..."
    )

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        answer = hr_assistant(prompt)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

    st.markdown("---")

    st.caption("Suggested questions")

    examples = [
        "Who are the top candidates?",
        "Show me Python Developer candidates",
        "How many candidates are shortlisted?",
        "What interviews are scheduled?",
        "Explain candidate scoring"
    ]

    for example in examples:

        if st.button(
            example,
            key="suggest_" + example
        ):

            st.session_state.messages.append({
                "role": "user",
                "content": example
            })

            st.session_state.messages.append({
                "role": "assistant",
                "content": hr_assistant(example)
            })

            st.rerun()


# ==========================================
# 15. FOOTER
# ==========================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#8290A5;font-size:12px;">
        SmartHire AI | Intelligent Talent Acquisition Platform<br>
        Built with Python, Streamlit and Plotly
    </div>
    """,
    unsafe_allow_html=True
)
