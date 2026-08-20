import json
from src.extractor import SkillExtractor

def run_tests():
    extractor = SkillExtractor(data_dir="data")

    # Test Case 1: Exact test case from challenge prompt
    sample_text = "I worked in the AI/ML Department and worked with CNN Models using Python"
    print("--- Test 1: Challenge Example ---")
    print(f"Input: \"{sample_text}\"")
    result = extractor.extract(sample_text)
    print("Output (JSON):")
    print(json.dumps(result, indent=2))

    # Test Case 2: Aliases and complex terms
    test_text_2 = "Built full-stack web services using react, fastapi, and postgresql on AWS with docker."
    print("\n--- Test 2: Multi-word Aliases & Tech ---")
    print(f"Input: \"{test_text_2}\"")
    result_2 = extractor.extract(test_text_2)
    print(json.dumps(result_2, indent=2))

if __name__ == "__main__":
    run_tests()