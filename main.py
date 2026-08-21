import json
import os
from src.extractor import SkillExtractor
from src.parser import ResumeParser
from src.matcher import JobMatcher

def demo_part_1(extractor: SkillExtractor):
    print("\n" + "=" * 50)
    print("  PART 1: CONVERSATIONAL SKILL EXTRACTION")
    print("=" * 50)
    
    challenge_input = "I worked in the AI/ML Department and worked with CNN Models using Python"
    print(f"Sample Input:\n\"{challenge_input}\"\n")
    output = extractor.extract(challenge_input)
    print("Output (JSON):")
    print(json.dumps(output, indent=2))

def demo_part_2(matcher: JobMatcher):
    print("\n" + "=" * 50)
    print("  PART 2: RESUME PARSING & ROLE MATCHING")
    print("=" * 50)
    
    sample_file = "examples/sample_resume.txt"
    if os.path.exists(sample_file):
        resume_text = ResumeParser.extract_text(sample_file)
        print(f"Loaded Resume File: {sample_file}\n")
    else:
        resume_text = "I have experience with Python, PyTorch, CNN, and Deep Learning in AI/ML."
        print("Loaded Inline Sample Profile.\n")

    result = matcher.match_resume(resume_text)

    print("1. Extracted Candidate Profile:")
    print(json.dumps(result["extracted_candidate_data"], indent=2))
    
    print(f"\n2. Best Suggested Role: >>> {result['best_fit_role']} <<<")
    
    print("\n3. Role Match Breakdown:")
    for role in result["role_rankings"]:
        print(f"  • {role['role_title']} -> Match Score: {role['match_score']}%")
        print(f"    - Matched: {role['matched_skills']}")
        print(f"    - Missing: {role['missing_skills']}")

def main():
    extractor = SkillExtractor(data_dir="data")
    matcher = JobMatcher(roles_path="data/job_roles.json", data_dir="data")

    while True:
        print("\n" + "#" * 45)
        print("       AI RECRUITER - EVALUATION SUITE")
        print("#" * 45)
        print("1. Test Part 1 (Extraction)")
        print("2. Test Part 2 (Resume Matching)")
        print("3. Custom Text Input (Part 1)")
        print("4. Custom File Path Input (Part 2 .txt / .pdf)")
        print("5. Exit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            demo_part_1(extractor)
        elif choice == "2":
            demo_part_2(matcher)
        elif choice == "3":
            user_input = input("\nEnter conversational sentence: ")
            print("\nResult:")
            print(json.dumps(extractor.extract(user_input), indent=2))
        elif choice == "4":
            path = input("\nEnter path to .txt or .pdf file: ").strip()
            if os.path.exists(path):
                text = ResumeParser.extract_text(path)
                result = matcher.match_resume(text)
                print(json.dumps(result, indent=2))
            else:
                print("File not found! Check path.")
        elif choice == "5":
            print("\nTerminating program. Good luck!")
            break
        else:
            print("Invalid choice, please select 1-5.")

if __name__ == "__main__":
    main()