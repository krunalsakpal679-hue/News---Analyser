# backend/tests/integration/test_full_pipeline.py
import pytest
import asyncio
import time
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_digital_pdf_pipeline(async_client: AsyncClient, sample_pdf_bytes: bytes):
    # 1. POST /documents/upload
    files = {"file": ("test.pdf", sample_pdf_bytes, "application/pdf")}
    response = await async_client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    job_id = response.json()["job_id"]
    assert job_id is not None

    # 2. Poll for status
    start_time = time.time()
    status = "queued"
    while status not in ("complete", "failed") and time.time() - start_time < 60:
        resp = await async_client.get(f"/api/v1/documents/{job_id}/status")
        assert resp.status_code == 200
        status = resp.json()["status"]
        if status != "complete":
            await asyncio.sleep(2)

    assert status == "complete", f"Pipeline failed or timed out. Last status: {status}"

    # 4. GET /results
    resp = await async_client.get(f"/api/v1/documents/{job_id}/results")
    assert resp.status_code == 200
    data = resp.json()

    # 5. Assertions
    assert data["verdict"] in ("GOOD", "BAD", "NEUTRAL")
    scores = data["final_scores"]
    total_pct = scores["positive_pct"] + scores["negative_pct"] + scores["neutral_pct"]
    assert pytest.approx(total_pct, 0.1) == 100.0
    assert data["word_count"] > 0
    assert data["extraction_method"] == "pdfplumber"

@pytest.mark.asyncio
async def test_png_pipeline(async_client: AsyncClient, sample_png_bytes: bytes):
    files = {"file": ("test.png", sample_png_bytes, "image/png")}
    response = await async_client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    job_id = response.json()["job_id"]

    start_time = time.time()
    status = "queued"
    while status not in ("complete", "failed") and time.time() - start_time < 60:
        resp = await async_client.get(f"/api/v1/documents/{job_id}/status")
        status = resp.json()["status"]
        if status != "complete":
            await asyncio.sleep(2)

    assert status == "complete"
    
    resp = await async_client.get(f"/api/v1/documents/{job_id}/results")
    data = resp.json()
    assert data["extraction_method"] == "tesseract"
    assert isinstance(data["ocr_confidence"], float)

@pytest.mark.asyncio
async def test_upload_invalid_docx(async_client: AsyncClient):
    files = {"file": ("test.docx", b"invalid content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = await async_client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 422
    assert "Unsupported file type" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_oversized(async_client: AsyncClient):
    # Mocking an oversized file by content
    # In reality, this might be handled by Nginx or FastAPI's dependency
    large_content = b"0" * (51 * 1024 * 1024) # 51MB
    files = {"file": ("large.pdf", large_content, "application/pdf")}
    response = await async_client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 422
    assert "exceeds" in response.json()["detail"]

@pytest.mark.asyncio
async def test_status_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/v1/documents/nonexistent-uuid/status")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_results_before_complete(async_client: AsyncClient, sample_pdf_bytes: bytes):
    files = {"file": ("instant.pdf", sample_pdf_bytes, "application/pdf")}
    upload_resp = await async_client.post("/api/v1/documents/upload", files=files)
    job_id = upload_resp.json()["job_id"]
    
    # Immediate fetch should be 202
    resp = await async_client.get(f"/api/v1/documents/{job_id}/results")
    assert resp.status_code == 202

@pytest.mark.asyncio
async def test_delete_job(async_client: AsyncClient, sample_pdf_bytes: bytes):
    files = {"file": ("delete-test.pdf", sample_pdf_bytes, "application/pdf")}
    upload_resp = await async_client.post("/api/v1/documents/upload", files=files)
    job_id = upload_resp.json()["job_id"]
    
    # DELETE
    del_resp = await async_client.delete(f"/api/v1/documents/{job_id}")
    assert del_resp.status_code == 204
    
    # Verify 404
    get_resp = await async_client.get(f"/api/v1/documents/{job_id}/status")
    assert get_resp.status_code == 404
