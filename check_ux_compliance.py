import requests
import json
import sys

def check_ux_compliance(job_id):
    url = f"http://localhost:8000/api/v1/documents/{job_id}/results"
    try:
        response = requests.get(url)
        data = response.json()
        
        # Check for technical terms
        technical_terms = ['VADER', 'BERT', 'NLP', 'compound score']
        found_terms = []
        
        content_str = json.dumps(data)
        for term in technical_terms:
            if term.lower() in content_str.lower():
                found_terms.append(term)
        
        print(f"UX Compliance Check for Job {job_id}:")
        if not found_terms:
            print("SUCCESS: No technical terms found in the API response.")
        else:
            print(f"FAILURE: Technical terms found: {found_terms}")
            print(f"Content: {content_str}")

        # Check for 'compound' rename in UI logic (frontend work)
        # Note: API might still use 'compound' as key, which is fine if UI hides it.
        # But user said "Replace: 'compound score' -> 'Overall Tone'".
        # In the context of "visible to end users", this usually means the text label.
        
    except Exception as e:
        print(f"Error checking compliance: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_ux_compliance(sys.argv[1])
    else:
        print("Please provide a job ID.")
