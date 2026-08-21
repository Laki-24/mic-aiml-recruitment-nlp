import json
import os
from src.extractor import SkillExtractor

class JobMatcher:
    def __init__(self, roles_path="data/job_roles.json", data_dir="data"):
        # Reuse our Part 1 extractor to parse skills from resumes
        self.extractor = SkillExtractor(data_dir=data_dir)
        self.roles_path = roles_path
        self.job_roles = self._load_job_roles()

    def _load_job_roles(self):
        if not os.path.exists(self.roles_path):
            raise FileNotFoundError(f"Job roles file not found at: {self.roles_path}")
        with open(self.roles_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def match_resume(self, resume_text):
        # Step 1: Run the resume text through Part 1 entity extractor
        extracted = self.extractor.extract(resume_text)
        
        # Combine all found candidate items into a set for quick comparison
        candidate_skills = set(
            extracted["skill"] + extracted["technology"] + extracted["language"]
        )

        role_evaluations = []

        # Step 2: Compare candidate skills against each job role
        for role in self.job_roles:
            target_skills = set(role.get("required_skills", []) + role.get("preferred_technologies", []))
            
            # Python set operations: intersection for matched, difference for missing
            matched = sorted(list(candidate_skills.intersection(target_skills)))
            missing = sorted(list(target_skills.difference(candidate_skills)))

            # Calculate match score percentage
            if len(target_skills) > 0:
                match_percentage = round((len(matched) / len(target_skills)) * 100, 1)
            else:
                match_percentage = 0.0

            role_evaluations.append({
                "role_id": role["role_id"],
                "role_title": role["title"],
                "match_score": match_percentage,
                "matched_skills": matched,
                "missing_skills": missing
            })

        # Step 3: Sort roles with highest match score first
        ranked_roles = sorted(role_evaluations, key=lambda x: x["match_score"], reverse=True)
        
        if ranked_roles and ranked_roles[0]["match_score"] > 0:
            best_fit = ranked_roles[0]["role_title"]
        else:
            best_fit = "No direct match found"

        return {
            "extracted_candidate_data": extracted,
            "best_fit_role": best_fit,
            "role_rankings": ranked_roles
        }