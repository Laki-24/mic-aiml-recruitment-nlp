# mic-aiml-recruitment-nlp
# AI Recruiter - Rule-Based NLP Candidate Profiling & Job Matching

A deterministic NLP recruitment tool developed for the **MIC AIML Recruitment Challenge (Track 2: NLP + ChatBot)**. 

The project solves two key screening tasks without relying on external LLM APIs:
1. **Part 1 (Conversational Extraction):** Extracts and categorizes skills, technologies, and programming languages from informal candidate self-descriptions into standardized JSON.
2. **Part 2 (Resume Parsing & Job Role Matching):** Ingests multi-format resumes (`.pdf` / `.txt`), normalizes candidate competencies, ranks compatibility against target job descriptions, and highlights exact missing skills.

---

## Key Features

- **Zero-API Dependency:** Built entirely with deterministic, rule-based NLP using Python's `re`, `json`, and `pypdf`. Fast, free, and produces 100% reproducible results without hallucination risks.
- **Symbol-Safe Regex Tokenization:** Uses negative lookaround assertions to correctly isolate tech names with symbols (like `C++`, `C#`, and `AI/ML`) without misidentifying single-letter tokens like `C` inside words like `Cloud`.
- **Set-Theoretic Role Matching:** Computes explainable role compatibility using set intersection and difference, giving recruiters transparent match percentages and explicit skill gap reports.
- **Dual Interface:** Runs both as an interactive **Streamlit Web App** (with JSON download exports) and a lightweight **Terminal CLI**.

---

## Project Structure

```text
├── data/
│   ├── skills.json              # Canonical skills & alias dictionaries
│   ├── technologies.json        # Frameworks, tools, & library taxonomy
│   ├── languages.json           # Programming & query languages
│   └── job_roles.json           # Benchmark job profiles and requirements
├── src/
│   ├── __init__.py
│   ├── extractor.py             # Part 1: Regex-based entity extractor
│   ├── parser.py                # Resume text reader (.pdf / .txt) with fallback
│   └── matcher.py               # Part 2: Set-based candidate scoring engine
├── examples/                    # Sample resume files for testing
├── app.py                       # Streamlit web application
├── main.py                      # Terminal CLI runner
├── requirements.txt             # Minimal dependencies (pypdf, streamlit)
└── README.md

How It Works (Engineering Decisions)
1. Alias-to-Canonical Mapping (data/)
Candidates describe identical skills in different ways (e.g., "DL", "neural nets", and "Deep Learning"). We maintain taxonomy files in data/ where each canonical entry maps to an array of common abbreviations and aliases. This decouples vocabulary updates from the code.

2. Length-Priority Sorting
Before matching text, all aliases are sorted in descending order by character length. This ensures composite multi-word terms (e.g., "Convolutional Neural Network") are matched and claimed before shorter acronyms (e.g., "CNN").

3. Custom Lookarounds for Symbol-Heavy Tech Names
Standard regex word boundaries (\b) fail on technical terms containing special characters like +, #, and / because regex treats them as non-word delimiters. Furthermore, simple substring searches create false positives (matching "C" inside "Cloud" or "Docker").

To solve this, we implemented custom boundary lookarounds:

Python
pattern = rf"(?<![a-zA-Z0-9_#+]){escaped_alias}(?![a-zA-Z0-9_#+])"
This guarantees exact-token matching regardless of whether the skill name contains special symbols.

4. Deterministic Compatibility Scoring
Candidate skills and job role requirements are converted into mathematical sets. Scoring and gap analysis are calculated directly:

Matched Skills: Candidate Skills ∩ Role Required Skills

Missing Skills: Role Required Skills \ Candidate Skills

Match Score: (len(Matched) / len(Required)) * 100

Sample Outputs
Part 1: Conversational Extraction
Input: "I worked in the AI/ML Department and worked with CNN Models using Python"

Extracted JSON:

JSON
{
  "skill": [
    "AI/ML"
  ],
  "technology": [
    "CNN"
  ],
  "language": [
    "Python"
  ]
}
Part 2: Resume Match Output
Input Profile: Candidate with Python, PyTorch, CNN, Deep Learning, and Git.

Top Suggested Role: AI/ML Engineer (100.0% Compatibility)

Matched Skills: AI/ML, CNN, Deep Learning, PyTorch, Python

Missing Skills for Backend Developer: FastAPI, Docker, PostgreSQL

Edge Cases Handled
Misnamed/Corrupted PDFs: src/parser.py wraps pypdf stream ingestion with a fallback that gracefully decodes raw bytes as text if a plain .txt file was renamed with a .pdf extension.

Case & Spacing Normalization: Inputs are normalized to lowercase with regex whitespace stripping to prevent formatting discrepancies.

Deduplication: Candidate skill sets are deduplicated so repeating a keyword multiple times does not inflate match percentages.
