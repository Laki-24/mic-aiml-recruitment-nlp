import json
import os
import re

class SkillExtractor:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # Load our JSON vocabulary files into memory
        self.skills_db = self._load_json("skills.json")
        self.technologies_db = self._load_json("technologies.json")
        self.languages_db = self._load_json("languages.json")

    def _load_json(self, filename):
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find vocabulary file at: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _extract_category(self, text, taxonomy):
        matched = []
        lower_text = text.lower()

        for item in taxonomy:
            canonical = item["canonical"]
            aliases = item["aliases"]

            # Match longer phrases first (e.g. "convolutional neural network" before "cnn")
            sorted_aliases = sorted(aliases, key=len, reverse=True)

            for alias in sorted_aliases:
                escaped_alias = re.escape(alias.lower())

                # Boundary check: standard \b breaks on C++, C#, and AI/ML symbols.
                # This lookaround also stops single letters like 'C' from matching inside 'Cat' or 'Code'.
                pattern = rf"(?<![a-zA-Z0-9_#+]){escaped_alias}(?![a-zA-Z0-9_#+])"

                if re.search(pattern, lower_text):
                    if canonical not in matched:
                        matched.append(canonical)
                    break  # Found this skill, move to the next item

        return matched

    def extract(self, text):
        return {
            "skill": self._extract_category(text, self.skills_db),
            "technology": self._extract_category(text, self.technologies_db),
            "language": self._extract_category(text, self.languages_db)
        }