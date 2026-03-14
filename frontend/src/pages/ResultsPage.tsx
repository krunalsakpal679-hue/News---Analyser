// src/pages/ResultsPage.tsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getResults, apiClient } from '../api/client';
import config from '../config';
import { useAnalysisStore } from '../store/analysisStore';
import { VerdictBadge } from '../components/results/VerdictBadge';
import { SentimentCharts } from '../components/results/SentimentCharts';
import { MetadataStrip } from '../components/results/MetadataStrip';
import { ExtractedText } from '../components/results/ExtractedText';
import { VerdictExplanation } from '../components/results/VerdictExplanation';
import { ArrowLeft, Share2, RefreshCcw, Loader2, ShieldCheck, Zap, Image as ImageIcon, RotateCcw, AlertTriangle, Copy, Check } from 'lucide-react';

export const ResultsPage: React.FC = () => {
    const { jobId } = useParams<{ jobId: string }>();
    const navigate = useNavigate();
    const { results, setResults, history, setHistory } = useAnalysisStore();
    const [loading, setLoading] = useState(!results || results.job_id !== jobId);
    const [retrying, setRetrying] = useState(false);
    const [copied, setCopied] = useState(false);

    const fetchResults = async () => {
        if (!jobId) return;
        try {
            const data = await getResults(jobId);
            setResults(data);
            
            // Auto-save to local history
            const historyItem = {
                job_id: data.job_id,
                filename: data.file_meta?.filename || 'Unnamed Doc',
                verdict: data.verdict,
                verdict_confidence: data.verdict_confidence,
                created_at: new Date().toISOString(),
                status: data.status
            };
            
            const existing = history.find(h => h.job_id === data.job_id);
            if (!existing) {
                const newHistory = [historyItem, ...history].slice(0, 50);
                setHistory(newHistory);
                localStorage.setItem('newsense_history', JSON.stringify(newHistory));
            }
        } catch (err) {
            console.error('Failed to fetch results', err);
            if (!retrying && import.meta.env.VITE_DEMO_MODE !== 'true') navigate('/');
        } finally {
            setLoading(false);
            setRetrying(false);
        }
    };

    useEffect(() => {
        if (!results || results.job_id !== jobId || (results.status === 'complete' && results.raw_text === null)) {
            fetchResults();
        } else {
            setLoading(false);
        }
    }, [jobId, results, setResults, navigate]);

    // Polling if retrying
    useEffect(() => {
        let interval: any;
        if (retrying || (results && results.status !== 'complete' && results.status !== 'failed' && import.meta.env.VITE_DEMO_MODE !== 'true')) {
            interval = setInterval(fetchResults, 3000);
        }
        return () => clearInterval(interval);
    }, [retrying, results]);

    const handleRetryDeep = async () => {
        if (!jobId) return;
        setRetrying(true);
        try {
            await apiClient.post(`/api/v1/documents/${jobId}/retry-deep`);
        } catch (err) {
            console.error('Retry failed', err);
            setRetrying(false);
        }
    };

    const handleCopyText = () => {
        const text = results?.extracted_text || results?.raw_text || '';
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    // Improve the loading condition: If results exist but status is not complete, 
    // keep showing the loader to prevent the "Uncertain News" flicker.
    const isProcessing = results && results.status !== 'complete' && results.status !== 'failed';
    
    if (loading || !results || (isProcessing && !results.verdict)) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <div className="flex flex-col items-center gap-6">
                    <div className="relative">
                        <Loader2 className="w-16 h-16 text-indigo-600 animate-spin" />
                        <Zap className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-indigo-400" />
                    </div>
                    <div className="text-center">
                        <p className="font-black text-slate-800 uppercase tracking-widest text-sm mb-1">
                            {isProcessing ? 'Finalizing Analysis' : 'Processing Analysis'}
                        </p>
                        <p className="text-xs text-slate-400 font-bold uppercase tracking-widest leading-relaxed">
                            {isProcessing ? 'Generating Verdict & Charts...' : 'Applying Neural Preprocessing...'}
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    const warnings = results.warnings || [];
    if (results.ocr_confidence !== null && results.ocr_confidence < 0.5) warnings.push('Low OCR Confidence');
    
    const showRetry = (results.word_count || 0) < 10 || (results.ocr_confidence || 0) < 0.5;

    const API_BASE = config.apiUrl;

    return (
        <div className="min-h-screen bg-[#F8FAFC] py-12 px-4 md:px-8">
            <div className="max-w-7xl mx-auto space-y-10">
                {/* Global Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/')}
                            className="group flex items-center gap-3 text-slate-500 hover:text-indigo-600 font-black transition-all"
                        >
                            <div className="p-3 bg-white rounded-2xl shadow-sm group-hover:bg-indigo-50 group-hover:shadow-md transition-all border border-slate-100">
                                <ArrowLeft className="w-5 h-5" />
                            </div>
                            <span className="uppercase tracking-[0.2em] text-[11px]">Home</span>
                        </button>
                        
                        <button
                            onClick={() => navigate('/comparison')}
                            className="group flex items-center gap-3 text-slate-500 hover:text-indigo-600 font-black transition-all border-l border-slate-200 pl-4"
                        >
                            <span className="uppercase tracking-[0.2em] text-[11px]">Back to Comparison</span>
                        </button>
                    </div>

                    <div className="flex items-center gap-4">
                         {showRetry && import.meta.env.VITE_DEMO_MODE !== 'true' && (
                            <button
                                onClick={handleRetryDeep}
                                disabled={retrying}
                                className={`flex items-center gap-2 px-6 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all ${retrying ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-amber-100 text-amber-700 hover:bg-amber-200 border border-amber-200 shadow-sm'}`}
                            >
                                <RotateCcw className={`w-4 h-4 ${retrying ? 'animate-spin' : ''}`} />
                                {retrying ? 'Retrying Scan...' : 'Run Deep OCR Scan'}
                            </button>
                        )}
                        <button 
                            onClick={handleCopyText}
                            className="flex items-center gap-2 p-3.5 bg-white rounded-2xl shadow-sm hover:shadow-md transition-all text-slate-400 hover:text-indigo-600 border border-slate-100"
                            title="Copy Extracted Text"
                        >
                            {copied ? <Check className="w-5 h-5 text-emerald-500" /> : <Copy className="w-5 h-5" />}
                        </button>
                        <button className="flex items-center gap-2 p-3.5 bg-white rounded-2xl shadow-sm hover:shadow-md transition-all text-slate-400 hover:text-indigo-600 border border-slate-100">
                            <Share2 className="w-5 h-5" />
                        </button>
                        <button
                            onClick={() => navigate('/')}
                            className="flex items-center gap-2 px-8 py-4 bg-slate-900 text-white font-black rounded-2xl shadow-xl shadow-slate-200 hover:bg-black transition-all hover:scale-[1.02] active:scale-[0.98] uppercase tracking-[0.1em] text-xs"
                        >
                            <RefreshCcw className="w-4 h-4" />
                            Launch New Scan
                        </button>
                    </div>
                </div>

                {/* Verdict Hero - Centerpiece */}
                <VerdictBadge
                    verdict={(results.verdict || 'UNCERTAIN') as any}
                    confidence={results.verdict_confidence || 0}
                    summary={results.explanation?.summary}
                    mainIdea={results.explanation?.main_idea}
                    keywords={results.explanation?.keywords}
                />

                {/* Massive 3-Column Intelligence Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                    
                    {/* Primary Analytics Column (Left) */}
                    <div className="lg:col-span-8 space-y-8">
                        {/* Sentiment Hub */}
                        <SentimentCharts scores={results.final_scores || { positive_pct: 0, negative_pct: 0, neutral_pct: 0, compound: 0 }} />
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {/* Document Preview Card */}
                            <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100 overflow-hidden flex flex-col">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-2.5 bg-slate-50 rounded-xl">
                                        <ImageIcon className="w-5 h-5 text-slate-400" />
                                    </div>
                                    <h3 className="text-slate-800 font-black uppercase tracking-[0.1em] text-xs">Uploaded Document Preview</h3>
                                </div>
                                <div className="flex-1 min-h-[300px] bg-slate-50 rounded-2xl border border-slate-100 overflow-hidden relative group">
                                    <img 
                                        src={`${API_BASE}/api/v1/documents/${jobId}/preview`} 
                                        alt="Document Preview" 
                                        className="w-full h-full object-contain transition-transform group-hover:scale-105 duration-500"
                                    />
                                    <div className="absolute inset-0 bg-slate-900/0 group-hover:bg-slate-900/10 transition-colors pointer-events-none" />
                                </div>
                            </div>

                            {/* Why this result? (Rationale) */}
                             <VerdictExplanation
                                explanation={results.explanation}
                                verdict={(results.verdict || 'UNCERTAIN') as any}
                                confidence={results.verdict_confidence || 0}
                                wordCount={results.word_count || 0}
                                ocrConfidence={results.ocr_confidence}
                                language={results.detected_language}
                            />
                        </div>

                        {/* Extracted Intel Block */}
                        <ExtractedText
                            text={results.extracted_text || results.raw_text || results.clean_text || ''}
                            wordCount={results.word_count || 0}
                            method={results.extraction_method}
                            ocrConfidence={results.ocr_confidence}
                            language={results.detected_language}
                        />
                    </div>

                    {/* Meta Intelligence Column (Right) */}
                    <div className="lg:col-span-4 space-y-8">
                        {/* Truth Score Orbit */}
                        <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100 overflow-hidden relative group">
                            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-50 rounded-full -translate-y-12 translate-x-12 opacity-50 group-hover:scale-110 transition-transform duration-700" />
                            <h3 className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px] mb-8 relative z-10">AI Confidence Rating</h3>
                            <div className="flex flex-col items-center py-6 relative z-10">
                                <div className="relative w-44 h-44 flex items-center justify-center mb-8">
                                    <svg className="w-full h-full -rotate-90">
                                        <circle
                                            cx="88"
                                            cy="88"
                                            r="80"
                                            fill="transparent"
                                            stroke="#f8fafc"
                                            strokeWidth="16"
                                        />
                                        <circle
                                            cx="88"
                                            cy="88"
                                            r="80"
                                            fill="transparent"
                                            stroke={results.verdict_confidence && results.verdict_confidence > 0.8 ? '#10b981' : (results.verdict_confidence && results.verdict_confidence > 0.5 ? '#6366f1' : '#f59e0b')}
                                            strokeWidth="16"
                                            strokeDasharray={502.6}
                                            strokeDashoffset={502.6 - (502.6 * (results.verdict_confidence || 0))}
                                            strokeLinecap="round"
                                            className="transition-all duration-1000 ease-out"
                                        />
                                    </svg>
                                    <div className="absolute flex flex-col items-center">
                                        <span className="text-5xl font-black text-slate-900 tracking-tighter leading-none">
                                            {Math.round((results.verdict_confidence || 0) * 100)}%
                                        </span>
                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mt-2">Analysis Level</span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2.5 px-6 py-2 bg-indigo-50 text-indigo-700 text-[10px] font-black uppercase tracking-[0.15em] rounded-full border border-indigo-100">
                                    <ShieldCheck className="w-4 h-4" />
                                    <span>Signal Verified</span>
                                </div>
                            </div>
                        </div>

                        {/* OCR Quality Suggestion Box */}
                        {results.ocr_confidence !== null && results.ocr_confidence < 0.6 && (
                            <div className="bg-amber-50 p-8 rounded-[2rem] border border-amber-200 shadow-sm space-y-4">
                                <div className="flex items-center gap-3">
                                    <AlertTriangle className="w-5 h-5 text-amber-600" />
                                    <h4 className="text-amber-800 font-black uppercase tracking-widest text-[10px]">Low Scan Quality Detected</h4>
                                </div>
                                <ul className="space-y-2">
                                    {['Increase image resolution', 'Crop to article area only', 'Improve lighting / remove glare'].map((s, i) => (
                                        <li key={i} className="flex items-center gap-2 text-xs font-bold text-amber-700/80">
                                            <div className="w-1 h-1 bg-amber-400 rounded-full" />
                                            {s}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Metadata summary */}
                        <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100">
                            <h3 className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px] mb-8">Detailed Metadata</h3>
                            <MetadataStrip
                                wordCount={results.word_count || 0}
                                language={results.detected_language || 'Unknown'}
                                duration={results.processing_ms_total ? results.processing_ms_total / 1000 : 1.2}
                                warnings={warnings}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
