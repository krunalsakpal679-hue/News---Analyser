// src/components/results/VerdictBadge.tsx
import React from 'react';
import { CheckCircle2, XCircle, MinusCircle, ShieldCheck, HelpCircle, AlignLeft, Sparkles, AlertCircle } from 'lucide-react';

interface VerdictBadgeProps {
    verdict: 'GOOD' | 'BAD' | 'NEUTRAL' | 'UNCERTAIN';
    confidence: number;
    summary?: string;
    mainIdea?: string;
    keywords?: {
        positive_words: string[];
        negative_words: string[];
        pos_count: number;
        neg_count: number;
    };
}

const VERDICT_THEMES = {
    GOOD: {
        bg: 'bg-emerald-50 border-emerald-200 shadow-emerald-100',
        icon: <CheckCircle2 className="w-16 h-16 text-emerald-500" />,
        label: 'GOOD NEWS',
        textColor: 'text-emerald-800',
        blob: 'bg-emerald-400',
        glow: 'shadow-emerald-200/50',
    },
    BAD: {
        bg: 'bg-rose-50 border-rose-200 shadow-rose-100',
        icon: <XCircle className="w-16 h-16 text-rose-500" />,
        label: 'BAD NEWS',
        textColor: 'text-rose-800',
        blob: 'bg-rose-400',
        glow: 'shadow-rose-200/50',
    },
    NEUTRAL: {
        bg: 'bg-amber-50 border-amber-200 shadow-amber-100',
        icon: <MinusCircle className="w-16 h-16 text-amber-500" />,
        label: 'NEUTRAL NEWS',
        textColor: 'text-amber-800',
        blob: 'bg-amber-400',
        glow: 'shadow-amber-200/50',
    },
    UNCERTAIN: {
        bg: 'bg-amber-50 border-amber-200 shadow-amber-100',
        icon: <HelpCircle className="w-16 h-16 text-amber-500" />,
        label: 'UNCERTAIN NEWS',
        textColor: 'text-amber-800',
        blob: 'bg-amber-400',
        glow: 'shadow-amber-200/50',
    }
};

export const VerdictBadge: React.FC<VerdictBadgeProps> = ({ verdict, confidence, summary, mainIdea, keywords }) => {
    const theme = VERDICT_THEMES[verdict] || VERDICT_THEMES.UNCERTAIN;
    
    // Emotion detection based on confidence and keywords
    const getEmotion = () => {
        if (verdict === 'GOOD') return 'Optimistic';
        if (verdict === 'BAD') return 'Critical / Sensational';
        if (verdict === 'NEUTRAL') return 'Objective';
        return 'Ambiguous';
    };

    return (
        <div className={`w-full p-10 md:p-14 rounded-[3rem] border-2 shadow-2xl flex flex-col items-center text-center transition-all ${theme.bg} ${theme.glow}`}>
            <div className="relative mb-10">
                <div className={`absolute inset-0 blur-3xl opacity-30 animate-pulse ${theme.blob}`} />
                <div className="relative z-10 p-8 bg-white rounded-full shadow-2xl border-4 border-white/50">
                    {theme.icon}
                </div>
            </div>

            <h1 className={`text-6xl md:text-8xl font-black mb-6 uppercase tracking-[-0.05em] ${theme.textColor}`}>
                {theme.label}
            </h1>

            <div className="flex flex-wrap items-center justify-center gap-4 mb-10">
                <div className="flex items-center gap-2 px-6 py-2.5 bg-white/70 backdrop-blur-md rounded-full border border-white/50 shadow-sm">
                    <ShieldCheck className={`w-5 h-5 ${theme.textColor}`} />
                    <span className={`text-base font-black ${theme.textColor} uppercase tracking-widest`}>
                        {Math.round(confidence * 100)}% Confidence
                    </span>
                </div>
                <div className="flex items-center gap-2 px-6 py-2.5 bg-white/70 backdrop-blur-md rounded-full border border-white/50 shadow-sm">
                    <Sparkles className={`w-5 h-5 ${theme.textColor}`} />
                    <span className={`text-base font-black ${theme.textColor} uppercase tracking-widest`}>
                        Emotion: {getEmotion()}
                    </span>
                </div>
            </div>

            <div className="max-w-4xl w-full space-y-10">
                {mainIdea && (
                    <div className="bg-white/40 backdrop-blur-sm p-8 rounded-[2.5rem] border border-white/60 text-left shadow-inner">
                        <div className="flex items-center gap-3 mb-4">
                            <div className={`p-1.5 rounded-lg ${theme.bg} border border-white/40`}>
                                <AlignLeft className={`w-5 h-5 ${theme.textColor} opacity-80`} />
                            </div>
                            <h4 className={`text-xs font-black uppercase tracking-[0.2em] ${theme.textColor} opacity-60`}>Main Idea</h4>
                        </div>
                        <p className={`text-2xl font-bold leading-snug ${theme.textColor}`}>
                            {mainIdea}
                        </p>
                    </div>
                )}

                {summary && (
                    <div className="relative py-6">
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-16 h-1.5 bg-current opacity-10 rounded-full" />
                        <p className="text-xl md:text-2xl text-slate-600/90 leading-relaxed italic px-6 font-medium">
                           "{summary}"
                        </p>
                    </div>
                )}
            </div>

            {keywords && (keywords.pos_count > 0 || keywords.neg_count > 0) ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-3xl mt-10">
                    <div className="bg-white/40 p-6 rounded-3xl border border-emerald-200/50 shadow-sm group hover:scale-[1.02] transition-transform">
                        <div className="text-4xl font-black text-emerald-600 mb-2">{keywords.pos_count}</div>
                        <div className="text-[10px] font-black text-emerald-700/70 uppercase tracking-[0.2em]">Positive Triggers</div>
                        {keywords.positive_words.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-5 justify-center">
                                {keywords.positive_words.slice(0, 8).map(w => (
                                    <span key={w} className="px-3 py-1.5 bg-emerald-100/80 text-emerald-700 text-[11px] font-bold rounded-xl border border-emerald-200/50">
                                        {w}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                    <div className="bg-white/40 p-6 rounded-3xl border border-rose-200/50 shadow-sm group hover:scale-[1.02] transition-transform">
                        <div className="text-4xl font-black text-rose-600 mb-2">{keywords.neg_count}</div>
                        <div className="text-[10px] font-black text-rose-700/70 uppercase tracking-[0.2em]">Negative Triggers</div>
                        {keywords.negative_words.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-5 justify-center">
                                {keywords.negative_words.slice(0, 8).map(w => (
                                    <span key={w} className="px-3 py-1.5 bg-rose-100/80 text-rose-700 text-[11px] font-bold rounded-xl border border-rose-200/50">
                                        {w}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <div className="mt-10 flex items-center gap-3 px-8 py-4 bg-slate-100/50 rounded-2xl border border-slate-200/50">
                   <AlertCircle className="w-5 h-5 text-slate-400" />
                   <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">No significant emotional triggers detected</p>
                </div>
            )}
        </div>
    );
};
