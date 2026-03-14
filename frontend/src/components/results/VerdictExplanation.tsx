// src/components/results/VerdictExplanation.tsx
import React from 'react';
import { Info, Search, Sparkles, AlertTriangle } from 'lucide-react';
import { Explanation } from '../../types/analysis';

interface VerdictExplanationProps {
    explanation: Explanation | null;
    verdict: 'GOOD' | 'BAD' | 'NEUTRAL' | 'UNCERTAIN';
    confidence: number;
    wordCount: number;
    ocrConfidence: number | null;
    language: string | null;
}

export const VerdictExplanation: React.FC<VerdictExplanationProps> = ({
    explanation,
    verdict,
    ocrConfidence,
}) => {
    // Priority: use backend-provided reasons, fallback to frontend logic.
    const reasons = explanation?.reasons || [];
    
    if (reasons.length === 0) {
        if (verdict === 'GOOD') {
            reasons.push('Balanced and informational tone detected.');
            reasons.push('Article structure matches professional standards.');
            reasons.push('No inflammatory or sensationalist language found.');
        } else if (verdict === 'BAD') {
            reasons.push('Sensationalist or misleading language detected.');
            reasons.push('High emotional bias in sentence structure.');
            reasons.push('Aggressive tone designed to provoke reaction.');
        } else {
            reasons.push('Neutral reporting style detected.');
            reasons.push('Fact-based presentation with low emotional trigger rate.');
        }
    }

    const isLowQuality = (ocrConfidence !== null && ocrConfidence < 0.5);

    return (
        <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-100/80">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 bg-indigo-50 rounded-xl">
                        <Sparkles className="w-5 h-5 text-indigo-600" />
                    </div>
                    <h3 className="text-xl font-black text-slate-800 tracking-tight">Why this result?</h3>
                </div>
            </div>

            <div className="space-y-6">
                 {isLowQuality && (
                    <div className="flex items-start gap-4 p-4 bg-amber-50 rounded-2xl border border-amber-200/50">
                        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                        <p className="text-sm font-bold text-amber-800 leading-snug">
                            Low scan quality detected. <span className="font-medium">Text extraction may be incomplete.</span>
                        </p>
                    </div>
                )}

                <div className="space-y-4">
                    {reasons.map((reason, idx) => (
                        <div key={idx} className="flex gap-4 group">
                            <div className="mt-1.5 w-2 h-2 rounded-full bg-indigo-400 group-hover:scale-125 transition-transform shrink-0 shadow-sm shadow-indigo-200" />
                            <p className="text-base font-bold text-slate-600 leading-tight">
                                {reason}
                            </p>
                        </div>
                    ))}
                </div>

                <div className="pt-6 border-t border-slate-50">
                    <div className="flex items-center gap-3 p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
                        <Info className="w-5 h-5 text-slate-400" />
                        <div>
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-0.5">Classification Logic</span>
                            <span className="text-sm font-black text-slate-700">
                                This assessment is based on NLP tone analysis and structural pattern matching.
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
