"""sync_jobs_table

Revision ID: 69cd4043b462
Revises: 0b82792ecc59
Create Date: 2026-03-15 02:48:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '69cd4043b462'
down_revision: Union[str, None] = '0b82792ecc59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add flattened result columns to analysis_jobs
    op.add_column('analysis_jobs', sa.Column('raw_text', sa.Text(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('clean_text', sa.Text(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('word_count', sa.Integer(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('ocr_confidence', sa.Float(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('extraction_method', sa.String(length=50), nullable=True))
    op.add_column('analysis_jobs', sa.Column('detected_language', sa.String(length=10), nullable=True))
    op.add_column('analysis_jobs', sa.Column('verdict', sa.String(length=20), nullable=True))
    op.add_column('analysis_jobs', sa.Column('verdict_confidence', sa.Float(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('positive_pct', sa.Float(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('negative_pct', sa.Float(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('neutral_pct', sa.Float(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('compound', sa.Float(), nullable=True))
    op.add_column('analysis_jobs', sa.Column('explanation', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('analysis_jobs', 'explanation')
    op.drop_column('analysis_jobs', 'compound')
    op.drop_column('analysis_jobs', 'neutral_pct')
    op.drop_column('analysis_jobs', 'negative_pct')
    op.drop_column('analysis_jobs', 'positive_pct')
    op.drop_column('analysis_jobs', 'verdict_confidence')
    op.drop_column('analysis_jobs', 'verdict')
    op.drop_column('analysis_jobs', 'detected_language')
    op.drop_column('analysis_jobs', 'extraction_method')
    op.drop_column('analysis_jobs', 'ocr_confidence')
    op.drop_column('analysis_jobs', 'word_count')
    op.drop_column('analysis_jobs', 'clean_text')
    op.drop_column('analysis_jobs', 'raw_text')
