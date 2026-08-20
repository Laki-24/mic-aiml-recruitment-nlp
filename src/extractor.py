import json
import os
import re
from typing import Dict, List, Any

class SkillExtractor:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.skills_db = self._load_json("skills.json")
        self.technologies_db = self._load_json("technologies.json")
        self.languages_db = self._load_json("languages.json")

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Taxonomy file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _extract_category(self, text: str, taxonomy: List[Dict[str, Any]]) -> List[str]:
        """
        Searches text for aliases and maps them to canonical names.
        Uses regex lookarounds to prevent false substring matches (e.g., 'Go' in 'Google').
        """
        matched_canonicals = []
        lowered_text = text.lower()

        for entry in taxonomy:
            canonical = entry["canonical"]
            aliases = entry["aliases"]

            # Sort aliases by length descending so multi-word phrases match before single words
            sorted_aliases = sorted(aliases, key=len, reverse=True)

            for alias in sorted_aliases:
                # \b doesn't work well on symbols like C++ or AI/ML, so we use lookarounds
                escaped_alias = re.escape(alias.lower())
                pattern = rf"(?<![a-zA-Z0-9_#+]){escaped_alias}(?![a-zA-Z0-9_#+])"
                
                if re.search(pattern, lowered_text):
                    matched_canonicals.append(canonical)
                    break  # Move to next entry once this canonical entity is matched

        # Return unique items maintaining appearance order
        return list(dict.fromkeys(matched_canonicals))

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts skills, technologies, and languages from unstructured conversational input.
        """
        return {
            "skill": self._extract_category(text, self.skills_db),
            "technology": self._extract_category(text, self.technologies_db),
            "language": self._extract_category(text, self.languages_db)
        }