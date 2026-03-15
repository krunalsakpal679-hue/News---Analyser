import { create } from 'zustand'

export interface AnalysisResult {
    job_id: string;
    verdict: 'GOOD' | 'BAD' | 'NEUTRAL' | null;
    verdict_confidence: number | null;
    filename: string;
    created_at: string;
    final_scores?: {
        compound: number;
        positive_pct: number;
        negative_pct: number;
        neutral_pct: number;
    };
    explanation?: {
        headline: string;
        summary: string;
        main_idea?: string;
        keywords: {
            positive_words: string[];
            negative_words: string[];
        };
    };
    status: string;
}

interface AppStore {
  // Navigation
  activeSection: 'upload' | 'single' | 'comparison' | 'history'
  setSection: (section: AppStore['activeSection']) => void

  // Upload mode
  uploadMode: 'single' | 'comparison'
  setUploadMode: (mode: 'single' | 'comparison') => void

  // Single result
  singleResult: AnalysisResult | null
  setSingleResult: (result: AnalysisResult | null) => void

  // Batch results — MUST be an array
  batchResults: AnalysisResult[]
  addBatchResult: (result: AnalysisResult) => void
  clearBatchResults: () => void

  // Processing
  isProcessing: boolean
  setProcessing: (v: boolean) => void

  // Error
  error: string | null
  setError: (err: string | null) => void
  clearError: () => void

  // Reset everything
  reset: () => void
}

const useAppStore = create<AppStore>((set) => ({
  activeSection: 'upload',
  setSection: (section) => set({ activeSection: section }),

  uploadMode: 'single',
  setUploadMode: (mode) => set({ uploadMode: mode }),

  singleResult: null,
  setSingleResult: (result) => set({ singleResult: result }),

  batchResults: [],
  addBatchResult: (result) => set((state) => ({
    batchResults: [...state.batchResults, result]
  })),
  clearBatchResults: () => set({ batchResults: [] }),

  isProcessing: false,
  setProcessing: (v) => set({ isProcessing: v }),

  error: null,
  setError: (err) => set({ error: err }),
  clearError: () => set({ error: null }),

  reset: () => set({
    activeSection: 'upload',
    uploadMode: 'single',
    singleResult: null,
    batchResults: [],
    isProcessing: false,
    error: null,
  }),
}))

export default useAppStore
