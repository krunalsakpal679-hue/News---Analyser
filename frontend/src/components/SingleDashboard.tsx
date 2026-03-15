import React from 'react';
import { VerdictBadge } from './results/VerdictBadge';
import { SentimentCharts } from './results/SentimentCharts';
import { MetadataStrip } from './results/MetadataStrip';
import { ExtractedText } from './results/ExtractedText';
import { VerdictExplanation } from './results/VerdictExplanation';
import { ShieldCheck, Image as ImageIcon, AlertTriangle } from 'lucide-react';

interface SingleDashboardProps {
  result: any;
}

const SingleDashboard: React.FC<SingleDashboardProps> = ({ result }) => {
    if (!result) return null;

    const warnings = result.warnings || [];
    if (result.ocr_confidence !== null && result.ocr_confidence < 0.5) warnings.push('Low OCR Confidence');
    
    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Verdict Hero */}
            <VerdictBadge
                verdict={(result.verdict || 'UNCERTAIN') as any}
                confidence={result.verdict_confidence || 0}
                summary={result.explanation?.summary}
                mainIdea={result.explanation?.main_idea}
                keywords={result.explanation?.keywords}
            />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left Column */}
                <div className="lg:col-span-8 space-y-8">
                    <SentimentCharts scores={result.final_scores || { positive_pct: 0, negative_pct: 0, neutral_pct: 0, compound: 0 }} />
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100 flex flex-col">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2.5 bg-slate-50 rounded-xl">
                                    <ImageIcon className="w-5 h-5 text-slate-400" />
                                </div>
                                <h3 className="text-slate-800 font-black uppercase tracking-[0.1em] text-xs">Document Preview</h3>
                            </div>
                            <div className="flex-1 min-h-[300px] bg-slate-50 rounded-2xl border border-slate-100 overflow-hidden relative">
                                <p className="absolute inset-0 flex items-center justify-center text-slate-300 font-bold p-10 text-center uppercase tracking-tighter text-2xl">Visual Archive Linked</p>
                            </div>
                        </div>

                         <VerdictExplanation
                            explanation={result.explanation}
                            verdict={(result.verdict || 'UNCERTAIN') as any}
                            confidence={result.verdict_confidence || 0}
                            wordCount={result.word_count || 0}
                            ocrConfidence={result.ocr_confidence}
                            language={result.detected_language}
                        />
                    </div>

                    <ExtractedText
                        text={result.extracted_text || result.raw_text || result.clean_text || ''}
                        wordCount={result.word_count || 0}
                        method={result.extraction_method}
                        ocrConfidence={result.ocr_confidence}
                        language={result.detected_language}
                    />
                </div>

                {/* Right Column */}
                <div className="lg:col-span-4 space-y-8">
                    <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100 relative group">
                        <h3 className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px] mb-8">AI Confidence Rating</h3>
                        <div className="flex flex-col items-center py-6">
                            <div className="relative w-44 h-44 flex items-center justify-center mb-8">
                                <svg className="w-full h-full -rotate-90">
                                    <circle cx="88" cy="88" r="80" fill="transparent" stroke="#f8fafc" strokeWidth="16" />
                                    <circle
                                        cx="88" cy="88" r="80" fill="transparent"
                                        stroke={result.verdict_confidence && result.verdict_confidence > 0.8 ? '#10b981' : (result.verdict_confidence && result.verdict_confidence > 0.5 ? '#6366f1' : '#f59e0b')}
                                        strokeWidth="16"
                                        strokeDasharray={502.6}
                                        strokeDashoffset={502.6 - (502.6 * (result.verdict_confidence || 0))}
                                        strokeLinecap="round"
                                        className="transition-all duration-1000 ease-out"
                                    />
                                </svg>
                                <div className="absolute flex flex-col items-center">
                                    <span className="text-5xl font-black text-slate-900 tracking-tighter leading-none">{Math.round((result.verdict_confidence || 0) * 100)}%</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-2.5 px-6 py-2 bg-indigo-50 text-indigo-700 text-[10px] font-black uppercase tracking-[0.15em] rounded-full border border-indigo-100">
                                <ShieldCheck className="w-4 h-4" />
                                <span>Signal Verified</span>
                            </div>
                        </div>
                    </div>

                    {result.ocr_confidence !== null && result.ocr_confidence < 0.6 && (
                        <div className="bg-amber-50 p-8 rounded-[2rem] border border-amber-200 shadow-sm space-y-4">
                            <div className="flex items-center gap-3">
                                <AlertTriangle className="w-5 h-5 text-amber-600" />
                                <h4 className="text-amber-800 font-black uppercase tracking-widest text-[10px]">Low Quality Detected</h4>
                            </div>
                        </div>
                    )}

                    <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100">
                        <h3 className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px] mb-8">Detailed Metadata</h3>
                        <MetadataStrip
                            wordCount={result.word_count || 0}
                            language={result.detected_language || 'Unknown'}
                            duration={result.processing_ms_total ? result.processing_ms_total / 1000 : 1.2}
                            warnings={warnings}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SingleDashboard;
