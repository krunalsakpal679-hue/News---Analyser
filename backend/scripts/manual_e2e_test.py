import asyncio
import httpx
import time
import os
import sys

# Ensure backend root is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

async def run_test():
    app_url = "http://localhost:8000"
    
    # Use existing PDF
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sample_news.pdf"))
    if not os.path.exists(pdf_path):
        print(f"ERROR: {pdf_path} not found")
        return
        
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    print("Uploading PDF...")
    async with httpx.AsyncClient(base_url=app_url, timeout=600.0) as client:
        # POST /documents/upload
        files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
        resp = await client.post("/api/v1/documents/upload", files=files)
        if resp.status_code != 201:
            print(f"FAILED: Status {resp.status_code}, {resp.text}")
            return
            
        job_id = resp.json()["job_id"]
        print(f"Job scheduled: {job_id}")
        
        # Poll for status
        start_time = time.time()
        while time.time() - start_time < 60:
            resp = await client.get(f"/api/v1/documents/{job_id}/status")
            status_data = resp.json()
            status = status_data["status"]
            progress = status_data["progress_pct"]
            print(f"Status: {status} ({progress}%)")
            
            if status == "complete":
                print("Pipeline COMPLETE!")
                break
            elif status == "failed":
                print(f"Pipeline FAILED: {status_data.get('error_message')}")
                return
            
            await asyncio.sleep(2)
        else:
            print("TIMED OUT")
            return
            
        # GET /results
        resp = await client.get(f"/api/v1/documents/{job_id}/results")
        results = resp.json()
        print("\n--- RESULTS ---")
        print(f"Verdict: {results['verdict']}")
        print(f"Confidence: {results['verdict_confidence']}%")
        print(f"Overall Tone: {results['final_scores']['positive_pct']}% / {results['final_scores']['negative_pct']}% / {results['final_scores']['neutral_pct']}%")
        print(f"Explanation: {results['explanation']['summary'] if results.get('explanation') else 'N/A'}")
        print("----------------\n")

if __name__ == "__main__":
    asyncio.run(run_test())
