import io
import json
import streamlit as st
from pypdf import PdfReader
from src.extractor import SkillExtractor
from src.matcher import JobMatcher

# App layout setup
st.set_page_config(page_title="AI Recruiter", page_icon="💼", layout="wide")

st.title("💼 AI Recruiter Assistant")
st.caption("Deterministic NLP Extraction & Role Matching (Built without LLM APIs)")

# Initialize our extraction and matching modules
extractor = SkillExtractor(data_dir="data")
matcher = JobMatcher(roles_path="data/job_roles.json", data_dir="data")

tab1, tab2 = st.tabs(["1: Extraction", "2: Matching"])

# PART 1: Conversational Skill Extraction

with tab1:
    st.header("Extract Skills from Experience Description")
    st.write("Pass conversational text to extract normalized skills, technologies, and languages.")

    default_text = "I worked in the AI/ML Department and worked with CNN Models using Python"
    user_input = st.text_area("Candidate Experience:", value=default_text, height=120)

    if st.button("Extract Entities", key="btn_part1", type="primary"):
        extracted_data = extractor.extract(user_input)

        st.subheader("Extracted Output (JSON)")
        st.json(extracted_data)

        # Let the user download the raw JSON result
        json_output = json.dumps(extracted_data, indent=2)
        st.download_button(
            label="📥 Download JSON Output",
            data=json_output,
            file_name="extracted_skills.json",
            mime="application/json",
            key="dl_part1"
        )

# PART 2: Resume Parsing & Job Matching

with tab2:
    st.header("Resume Analysis & Role Recommendation")
    st.write("Parse a resume (.pdf / .txt) to match candidate skills against predefined job roles.")

    input_choice = st.radio("Select Input Format:", ["Upload File (.pdf / .txt)", "Paste Raw Text"], horizontal=True)
    resume_content = ""

    if input_choice == "Upload File (.pdf / .txt)":
        uploaded_file = st.file_uploader("Upload candidate resume", type=["pdf", "txt"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".txt"):
                resume_content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            elif uploaded_file.name.endswith(".pdf"):
                try:
                    reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
                    pages = [p.extract_text() for p in reader.pages if p.extract_text()]
                    resume_content = "\n".join(pages).strip()

                    if not resume_content:
                        st.warning("No selectable text found in this PDF (it might be a scanned image).")
                except Exception:
                    # Fallback in case a renamed text file was uploaded as .pdf
                    resume_content = uploaded_file.getvalue().decode("utf-8", errors="ignore").strip()
    else:
        resume_content = st.text_area("Paste Resume Text Here:", height=200, placeholder="Paste candidate experience or resume text here...")

    if resume_content.strip():
        with st.expander("Show Extracted Resume Text"):
            st.text(resume_content)

        if st.button("Match Candidate with Roles", key="btn_part2", type="primary"):
            results = matcher.match_resume(resume_content)

            # 1. Best matching role display
            st.success(f"### Best Match: **{results['best_fit_role']}**")

            # 2. Match breakdown per role
            st.subheader("Role Compatibility Breakdown")
            for role in results["role_rankings"]:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric(label=role["role_title"], value=f"{role['match_score']}%")
                with col2:
                    matched_str = ", ".join(role["matched_skills"]) if role["matched_skills"] else "None"
                    missing_str = ", ".join(role["missing_skills"]) if role["missing_skills"] else "None"
                    st.write(f"**Matched Skills:** {matched_str}")
                    st.write(f"**Missing Skills:** {missing_str}")
                st.divider()

            # 3. Candidate extracted profile data
            st.subheader("Extracted Candidate Profile Data")
            st.json(results["extracted_candidate_data"])

            # 4. Download full report as JSON
            report_json = json.dumps(results, indent=2)
            st.download_button(
                label="📥 Download Full Match Report (JSON)",
                data=report_json,
                file_name="candidate_job_match_report.json",
                mime="application/json",
                key="dl_part2"
            )