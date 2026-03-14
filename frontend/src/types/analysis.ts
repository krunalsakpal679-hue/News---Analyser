// src/types/analysis.ts
/**
 * Shared data contracts for NewSense AI analysis pipeline.
 */

export type AnalysisStatus = 'queued' | 'extracting' | 'analyzing' | 'complete' | 'failed' | 'cleaning' | 'error';

export interface VADERScores {
    positive: number;
    negative: number;
    neutral: number;
    compound: number;
}

export interface BERTScores {
    positive: number;
    negative: number;
}

export interface FinalScores {
    positive_pct: number;
    negative_pct: number;
    neutral_pct: number;
    compound: number;
}

export interface FileMeta {
    filename: string;
    file_type: string;
    file_size: number;
    storage_key: string;
    page_count: number;
}

export interface PipelineError {
    stage: string;
    error_type: string;
    message: string;
    timestamp: string;
}

export interface Explanation {
    headline: string;
    summary: string;
    color: string;
    icon: string;
    main_idea?: string;
    reasons?: string[];
    keywords: {
        positive_words: string[];
        negative_words: string[];
        pos_count: number;
        neg_count: number;
    };
}

export interface AnalysisState {
    job_id: string;
    file_meta: FileMeta | null;
    raw_text: string | null;
    clean_text: string | null;
    extracted_text?: string | null;
    word_count: number | null;
    detected_language: string | null;
    ocr_confidence: number | null;
    extraction_method: 'pdfplumber' | 'tesseract' | null;
    vader_scores: VADERScores | null;
    bert_scores: BERTScores | null;
    final_scores: FinalScores | null;
    verdict: 'GOOD' | 'BAD' | 'NEUTRAL' | null;
    verdict_confidence: number | null;
    status: AnalysisStatus;
    errors: PipelineError[];
    warnings?: string[];
    progress_pct: number;
    processing_ms_total: number | null;
    explanation: Explanation | null;
    main_idea?: string | null;
    summary_short?: string | null;
}

export interface AnalysisHistoryItem {
    job_id: string;
    filename: string;
    verdict: 'GOOD' | 'BAD' | 'NEUTRAL' | null;
    verdict_confidence: number | null;
    created_at: string;
    status: AnalysisStatus;
}
