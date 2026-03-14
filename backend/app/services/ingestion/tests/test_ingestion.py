# backend/app/services/ingestion/tests/test_ingestion.py
import uuid
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from io import BytesIO
from fpdf import FPDF
from PIL import Image

from app.services.ingestion.validator import FileValidator
from app.services.ingestion.format_detector import FormatDetector
from app.services.ingestion.service import FileIngestionService

@pytest.fixture
def minimal_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(200, 10, text="This is a digital PDF with text content.", new_x='LMARGIN', new_y='NEXT', align='C')
    # Use output() to get bytes in fpdf2
    return pdf.output()

@pytest.fixture
def minimal_png_bytes():
    img = Image.new('RGB', (10, 10), color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

@pytest.fixture
def scanned_pdf_bytes():
    # PDF with an image but no text layer
    pdf = FPDF()
    pdf.add_page()
    img = Image.new('RGB', (100, 100), color='blue')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_data = img_byte_arr.getvalue()
    pdf.image(BytesIO(img_data), x=10, y=10, w=80)
    return pdf.output()

def test_validator_rejects_large_file():
    validator = FileValidator()
    # Mock settings.MAX_FILE_SIZE_MB
    with patch("app.services.ingestion.validator.settings.MAX_FILE_SIZE_MB", 1):
        validator.MAX_SIZE = 1 * 1024 * 1024
        errors = validator.validate("large.pdf", b"0" * (2 * 1024 * 1024))
        assert any("exceeds" in e for e in errors)

def test_validator_rejects_unsupported_mime():
    validator = FileValidator()
    # Use a dummy content that won't be identified as PDF/PNG/JPG
    errors = validator.validate("test.docx", b"PK\x03\x04 not a real docx but magic will check")
    assert any("Unsupported file type" in e for e in errors)

def test_format_detector_digital_pdf(minimal_pdf_bytes):
    detector = FormatDetector()
    fmt = detector.detect(minimal_pdf_bytes, "application/pdf")
    assert fmt == "pdf_digital"

def test_format_detector_scanned_pdf(scanned_pdf_bytes):
    detector = FormatDetector()
    fmt = detector.detect(scanned_pdf_bytes, "application/pdf")
    assert fmt == "pdf_scanned"

@pytest.mark.asyncio
async def test_ingestion_service_success(minimal_png_bytes):
    mock_storage = MagicMock()
    mock_storage.upload_file = AsyncMock(return_value="storage/path/test.png")
    
    mock_job_service = MagicMock()
    mock_job = MagicMock()
    mock_job.id = uuid.uuid4()
    mock_job_service.create_job = AsyncMock(return_value=mock_job)
    
    validator = FileValidator()
    detector = FormatDetector()
    
    service = FileIngestionService(mock_storage, mock_job_service, validator, detector)
    
    with patch("app.celery.run_full_pipeline.delay") as mock_delay:
        job_id, errors = await service.ingest("test.png", minimal_png_bytes)
        assert job_id != ""
        assert errors == []
        mock_delay.assert_called_once_with(job_id)
