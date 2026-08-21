import io
import json
import streamlit as st
from pypdf import PdfReader
from pypdf.errors import PdfStreamError
from src.extractor import SkillExtractor
from src.matcher import JobMatcher

st.set_page_config(page_title="AI Recruiter", page_icon="💼", layout="wide")

st.title("💼 AI Recruiter Assistant")
st.caption("Deterministic, Rule-Based NLP Extraction & Role Matching Engine (Zero LLM API Keys)")

tab1, tab2 = st.tabs(["Part 1: Conversational Extraction", "Part 2: Resume Role Matching"])

extractor = SkillExtractor(data_dir="data")
matcher = JobMatcher(roles_path="data/job_roles.json", data_dir="data")

# ==========================================
# PART 1: CONVERSATIONAL EXTRACTION
# ==========================================
with tab1:
    st.header("Part 1: Conversational Skill Extraction")
    st.write("Extract skills, technologies, and languages from unstructured conversational text.")
    
    default_text = "I worked in the AI/ML Department and worked with CNN Models using Python"
    user_input = st.text_area("Candidate Experience Input:", value=default_text, height=120)
    
    if st.button("Extract Entities", key="btn_part1", type="primary"):
        result = extractor.extract(user_input)
        
        st.subheader("Extracted Output")
        st.json(result)
        
        # Download JSON Button for Part 1
        json_str_p1 = json.dumps(result, indent=2)
        st.download_button(
            label="📥 Download JSON Output",
            data=json_str_p1,
            file_name="extracted_skills.json",
            mime="application/json",
            key="dl_part1"
        )

# ==========================================
# PART 2: RESUME MATCHING & SCORING
# ==========================================
with tab2:
    st.header("Part 2: Resume Parsing & Role Matching")
    st.write("Upload a resume or paste raw text to extract skills and compute job compatibility scores.")
    
    input_mode = st.radio("Choose Input Mode:", ["Upload Resume (.pdf / .txt)", "Paste Resume Text"], horizontal=True)
    resume_text = ""
    
    if input_mode == "Upload Resume (.pdf / .txt)":
        uploaded_file = st.file_uploader("Upload File", type=["pdf", "txt"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".txt"):
                resume_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            elif uploaded_file.name.endswith(".pdf"):
                try:
                    # Attempt binary PDF read
                    reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
                    extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                    resume_text = "\n".join(extracted_pages).strip()
                    
                    if not resume_text:
                        st.warning("PDF parsed, but no text was found (it may be an image scan).")
                except (PdfStreamError, Exception):
                    # Smart Fallback: Decode directly as text if file is a renamed .txt
                    resume_text = uploaded_file.getvalue().decode("utf-8", errors="ignore").strip()
    else:
        resume_text = st.text_area("Paste Full Resume Text:", height=200, placeholder="Paste resume content here...")

    if resume_text.strip():
        with st.expander("Preview Raw Extracted Text"):
            st.text(resume_text)
            
        if st.button("Analyze & Match Candidate", key="btn_part2", type="primary"):
            match_data = matcher.match_resume(resume_text)
            
            # 1. Top Recommended Role
            st.success(f"### Top Recommended Role: **{match_data['best_fit_role']}**")
            
            # 2. Role Compatibility Breakdown
            st.subheader("Role Compatibility Breakdown")
            for role in match_data["role_rankings"]:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric(label=role["role_title"], value=f"{role['match_score']}%")
                with col2:
                    st.write(f"**Matched Skills:** {', '.join(role['matched_skills']) if role['matched_skills'] else 'None'}")
                    st.write(f"**Missing Skills:** {', '.join(role['missing_skills']) if role['missing_skills'] else 'None'}")
                st.divider()

            # 3. Candidate Extracted Skills Display
            st.subheader("Extracted Candidate Profile Data")
            st.json(match_data["extracted_candidate_data"])
            
            # 4. Download Full Match Report as JSON
            json_str_p2 = json.dumps(match_data, indent=2)
            st.download_button(
                label="📥 Download Full Match Report (JSON)",
                data=json_str_p2,
                file_name="candidate_job_match_report.json",
                mime="application/json",
                key="dl_part2"
            )