// src/store/analysisStore.ts
import { create } from 'zustand';
import { AnalysisState, AnalysisHistoryItem } from '../types/analysis';

export const ANALYSIS_STATUS_LABELS: Record<AnalysisState['status'], string> = {
    extracting: 'Reading document...',
    cleaning: 'Processing text...',
    analyzing: 'Analyzing sentiment...',
    complete: 'Analysis complete!',
    failed: 'Analysis failed',
    error: 'Analysis error',
    queued: 'Waiting in queue...',
};

interface AnalysisStore {
    jobId: string | null;
    uploadedFile: File | null;
    status: AnalysisState['status'] | null;
    progressPct: number;
    results: AnalysisState | null;
    history: AnalysisHistoryItem[];

    // Actions
    setJobId: (id: string | null) => void;
    setFile: (file: File | null) => void;
    updateProgress: (status: AnalysisState['status'], progress: number) => void;
    setResults: (results: AnalysisState | null) => void;
    setHistory: (history: AnalysisHistoryItem[]) => void;
    reset: () => void;
}

export const useAnalysisStore = create<AnalysisStore>((set) => ({
    jobId: null,
    uploadedFile: null,
    status: null,
    progressPct: 0,
    results: null,
    history: [],

    setJobId: (id) => set({ jobId: id }),
    setFile: (file) => set({ uploadedFile: file }),
    updateProgress: (status, progress) => set({ status, progressPct: progress }),
    setResults: (results) => set({
        results,
        status: results?.status || 'complete' // Usually complete if getting results
    }),
    setHistory: (history) => set({ history }),
    reset: () => set({ jobId: null, uploadedFile: null, status: null, progressPct: 0, results: null }),
}));
