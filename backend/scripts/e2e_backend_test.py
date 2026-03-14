import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_pipeline():
    # 1. Upload
    print("--- Testing Upload ---")
    try:
        files = {'file': ('test.png', open('test.png', 'rb'), 'image/png')}
        r = httpx.post(f"{BASE_URL}/documents/upload", files=files, timeout=60.0)
    except Exception as e:
        print(f"X Connection error: {str(e)}")
        return

    if r.status_code != 201:
        print(f"X Upload failed: {r.status_code} - {r.text}")
        return
    
    job_id = r.json()['job_id']
    print(f"OK Upload success. Job ID: {job_id}")

    # 2. Poll Status
    print(f"--- Waiting for analysis (Max 120s)... ---")
    # Initialize resp to None or a default value before the loop
    resp = None 
    for i in range(1, 13):
        time.sleep(10)
        try:
            resp = httpx.get(f"{BASE_URL}/documents/{job_id}/status")
            status = resp.json().get('status')
            prog = resp.json().get('progress_pct', 0)
            print(f"Attempt {i} status: {status} ({prog}%)")
            
            if status == 'complete':
                print(f"OK! Analysis complete.")
                break
            if status == 'failed':
                print(f"FAILED! Error: {resp.json().get('error_message')}")
                break
        except Exception as e:
            print(f"Error polling status: {e}")
            break
    else:
        print("TIMED OUT waiting for analysis.")

    # 4. Check results if complete
    # Use the last 'resp' from the loop, or fetch again if loop didn't complete successfully
    if resp and resp.json()['status'] == 'complete':
        print("--- Fetching Results ---")
        r = httpx.get(f"{BASE_URL}/documents/{job_id}/results")
        if r.status_code == 200:
            print("OK Results retrieved successfully!")
            print(f"Verdict: {r.json().get('verdict')}")
        else:
            print(f"X Results fetch failed: {r.status_code}")
    else:
        print(f"X Pipeline stuck at: {r.json()['status']}")

if __name__ == "__main__":
    test_pipeline()
