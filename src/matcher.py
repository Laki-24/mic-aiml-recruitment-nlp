import json
import os
from typing import Dict, List, Any
from src.extractor import SkillExtractor

class JobMatcher:
    def __init__(self, roles_path: str = "data/job_roles.json", data_dir: str = "data"):
        self.extractor = SkillExtractor(data_dir=data_dir)
        self.roles_path = roles_path
        self.job_roles = self._load_job_roles()

    def _load_job_roles(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.roles_path):
            raise FileNotFoundError(f"Job roles file not found: {self.roles_path}")
        with open(self.roles_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def match_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyzes resume text, extracts skills, and ranks job role matches.
        """
        # Step 1: Extract candidate skills using Part 1 extractor
        extracted = self.extractor.extract(resume_text)
        
        # Combine all found items into a normalized set
        candidate_skills = set(
            extracted["skill"] + extracted["technology"] + extracted["language"]
        )

        role_evaluations = []

        # Step 2: Compare against every role in database
        for role in self.job_roles:
            target_skills = set(role["required_skills"] + role["preferred_technologies"])
            
            # Set intersection gives matching skills
            matched = sorted(list(candidate_skills.intersection(target_skills)))
            
            # Set difference gives missing required skills
            missing = sorted(list(target_skills.difference(candidate_skills)))

            # Score = (Matched / Total Required) * 100
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

        # Step 3: Sort by highest match score
        ranked_roles = sorted(role_evaluations, key=lambda x: x["match_score"], reverse=True)
        best_fit = ranked_roles[0]["role_title"] if ranked_roles and ranked_roles[0]["match_score"] > 0 else "No direct match found"

        return {
            "extracted_candidate_data": extracted,
            "best_fit_role": best_fit,
            "role_rankings": ranked_roles
        }