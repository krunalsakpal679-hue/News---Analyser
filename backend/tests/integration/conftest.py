# backend/tests/integration/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io

from app.main import app
from app.database import get_db
from app.models.base import Base
from app.config import settings

# Test Database URL
if settings.DATABASE_URL.startswith("sqlite"):
    TEST_DATABASE_URL = settings.DATABASE_URL.replace(".db", "_test.db")
else:
    TEST_DATABASE_URL = settings.DATABASE_URL.replace("/newsense", "/newsense_test")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session_factory = async_sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)
    session = session_factory()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()

@pytest.fixture
async def async_client(test_db) -> AsyncGenerator[AsyncClient, None]:
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def sample_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="This is a test document about positive economic news.", ln=True, align='L')
    pdf.cell(200, 10, txt="The stock market reached a record high today as corporate profits surged.", ln=True, align='L')
    pdf.cell(200, 10, txt="Analysts are optimistic about the future growth of the technology sector.", ln=True, align='L')
    return pdf.output()

@pytest.fixture
def sample_png_bytes():
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        # Try to use a default font if available, otherwise fallback
        font = ImageFont.load_default()
    except Exception:
        font = None
        
    text = "CRITICAL FAILURE: THE COMPANY ANNOUNCED MASSIVE DEBT.\n" \
           "Stock prices plummeted 40% overnight as investors fled.\n" \
           "The CEO has resigned effective immediately amid the scandal."
    
    d.text((50, 50), text, fill=(0, 0, 0), font=font)
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
