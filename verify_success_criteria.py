# verify_success_criteria.py
import asyncio
import requests
import websockets
import json
import time
import os
import sys

BASE_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/api/v1/ws"

async def test_upload_and_pipeline(filename, expected_retry_count=0):
    print(f"\n--- Testing Pipeline with file: {filename} ---")
    
    # 1. POST /upload
    with open("test.pdf", "rb") as f:
        files = {"file": (filename, f, "application/pdf")}
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        upload_duration = (time.time() - start_time) * 1000
    
    if response.status_code != 201:
        print(f"FAILED: Upload returned {response.status_code}")
        print(response.json())
        return False
    
    job_id = response.json()["job_id"]
    print(f"SUCCESS: Upload took {upload_duration:.2f}ms. Job ID: {job_id}")
    
    if upload_duration > 500:
        print("WARNING: Upload took longer than 500ms")
    
    # 2. WebSocket listener
    print(f"Connecting to WebSocket: {WS_URL}/{job_id}")
    events_received = []
    pipeline_start = time.time()
    
    try:
        async with websockets.connect(f"{WS_URL}/{job_id}") as ws:
            while True:
                msg = await ws.recv()
                event = json.loads(msg)
                events_received.append(event)
                print(f"Event: {event.get('event')} | Progress: {event.get('progress')}%")
                
                if event.get("event") == "complete":
                    break
                if event.get("event") == "error":
                    print(f"Pipeline Event (Error/Retry): {event.get('message')}")
                    # Don't break here, wait for subsequent retry success if possible
                    # But we should break if it's NOT a simulated retry (terminal failure)
                    if "Simulated retry-able failure" not in event.get('message', ''):
                        break
    except Exception as e:
        print(f"WebSocket closed/failed: {str(e)}")

    pipeline_duration = time.time() - pipeline_start
    print(f"Pipeline completed in {pipeline_duration:.2f} seconds")
    
    # 3. GET /results
    res_response = requests.get(f"{BASE_URL}/documents/{job_id}/results")
    if res_response.status_code == 200:
        data = res_response.json()
        print(f"Verdict: {data.get('verdict')} | Confidence: {data.get('verdict_confidence')}")
        if data.get('verdict'):
            print("SUCCESS: GET /results returned valid verdict")
    else:
        print(f"FAILED: GET /results returned {res_response.status_code}")

    return True

async def main():
    # Regular test
    await test_upload_and_pipeline("test.pdf")
    
    # Retry test (if worker is running and has the retry logic)
    # This will trigger 2 failures then succeed
    print("\n--- Starting Retry Verification ---")
    await test_upload_and_pipeline("retry_test.pdf")

if __name__ == "__main__":
    if True: # Always overwrite to ensure fresh content
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas("test.pdf", pagesize=letter)
        text = "Economic growth reaching new heights this quarter. " * 50 # ~500 words
        text += "The community is thriving and people are very happy with the recent developments and success. " * 10
        
        y = 750
        for line in [text[i:i+80] for i in range(0, len(text), 80)]:
            c.drawString(100, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                y = 750
        c.save()
        print("Created 500-word positive test document.")
        
    asyncio.run(main())
