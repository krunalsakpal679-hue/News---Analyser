# backend/tests/test_ocr.py
import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
from fpdf import FPDF

from app.services.ocr.preprocessor import ImagePreprocessor
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.tesseract_ocr import TesseractOCR
from app.services.ocr.pdf_extractor import PDFExtractor
from app.services.ocr.engine import OCREngine, ExtractionError

pytestmark = pytest.mark.asyncio(loop_scope="module")

@pytest.fixture
def text_image_bytes():
    """Generates a simple white PNG with 'Hello World'."""
    img = Image.new('RGB', (800, 200), color='white')
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
    d.text((10,10), "Hello World OCR Testing", fill=(0,0,0), font=font)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

@pytest.fixture
def digital_pdf_bytes():
    """Generates a basic digital PDF with known text."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, align='C', text="Hello PDF Pipeline")
    return bytearray(pdf.output())

def test_preprocess_from_bytes(text_image_bytes):
    preprocessor = ImagePreprocessor()
    processed = preprocessor.preprocess_from_bytes(text_image_bytes)
    assert isinstance(processed, np.ndarray)
    assert len(processed.shape) == 2

def test_column_detector():
    img = np.ones((1000, 800), dtype=np.uint8) * 255
    img[100:900, 100:300] = 0
    detector = ColumnDetector()
    columns = detector.detect_columns(img)
    assert len(columns) == 1
    
    img2 = np.ones((1000, 800), dtype=np.uint8) * 255
    img2[100:900, 100:300] = 0
    img2[100:900, 500:700] = 0
    columns2 = detector.detect_columns(img2)
    assert len(columns2) == 2

def test_tesseract_ocr_run(text_image_bytes):
    preprocessor = ImagePreprocessor()
    processed = preprocessor.preprocess_from_bytes(text_image_bytes)
    
    tesseract = TesseractOCR()
    result = tesseract.run(processed)
    assert 'Hello' in result['text']
    assert isinstance(result['confidence'], float)
    assert 0.0 <= result['confidence'] <= 1.0

def test_pdf_extractor_digital(digital_pdf_bytes):
    extractor = PDFExtractor()
    result = extractor.extract_digital(digital_pdf_bytes)
    assert 'Hello PDF Pipeline' in result['text'] or 'Hello PDF' in result['text']
    assert result['method'] == 'pdfplumber'
    assert result['page_count'] == 1
    assert result['confidence'] is None

async def test_ocr_engine_routes(digital_pdf_bytes):
    engine = OCREngine()
    result = await engine.extract("job123", digital_pdf_bytes, "pdf_digital")
    assert result['method'] == 'pdfplumber'
    assert 'Hello PDF' in result['text']

async def test_ocr_engine_empty_raises():
    engine = OCREngine()
    img = Image.new('RGB', (100, 100), color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    
    with pytest.raises(ExtractionError):
        await engine.extract("job123", img_byte_arr.getvalue(), "image_png")
