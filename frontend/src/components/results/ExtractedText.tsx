// src/components/results/ExtractedText.tsx
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Type, Cpu, FileText } from 'lucide-react';

interface ExtractedTextProps {
    text: string;
    wordCount: number;
    method: string | null;
    ocrConfidence: number | null;
    language: string | null;
}

export const ExtractedText: React.FC<ExtractedTextProps> = ({ text, wordCount, ocrConfidence, language }) => {
    return (
        <div className="w-full bg-[#0F172A] rounded-[2rem] overflow-hidden shadow-2xl border border-slate-800">
            <div className="p-8 border-b border-slate-800/50 bg-slate-900/50">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20">
                        <FileText className="w-6 h-6 text-indigo-400" />
                    </div>
                    <div>
                        <h3 className="font-black text-xl text-white tracking-tight">Extracted Content</h3>
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Digital Intelligence Transcription</p>
                    </div>
                </div>
            </div>

            <div className="p-8">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div className="bg-slate-800/40 p-4 rounded-2xl border border-slate-700/30">
                        <div className="text-[9px] text-slate-500 font-black uppercase tracking-widest mb-1.5 opacity-60">Volume</div>
                        <div className="text-xl font-black text-white">{wordCount} <span className="text-[10px] text-slate-500 font-medium">WORDS</span></div>
                    </div>
                    <div className="bg-slate-800/40 p-4 rounded-2xl border border-slate-700/30">
                        <div className="text-[9px] text-slate-500 font-black uppercase tracking-widest mb-1.5 opacity-60">Source Lang</div>
                        <div className="text-xl font-black text-white capitalize">{language || 'Unknown'}</div>
                    </div>
                    <div className="bg-slate-800/40 p-4 rounded-2xl border border-slate-700/30">
                        <div className="text-[9px] text-slate-500 font-black uppercase tracking-widest mb-1.5 opacity-60">Precision</div>
                        <div className="text-xl font-black text-white">{Math.round((ocrConfidence || 0) * 100)}%</div>
                    </div>
                     <div className="bg-slate-800/40 p-4 rounded-2xl border border-slate-700/30">
                        <div className="text-[9px] text-slate-500 font-black uppercase tracking-widest mb-1.5 opacity-60">Engine</div>
                        <div className="text-xl font-black text-white">OCR-V4</div>
                    </div>
                </div>

                <div className="relative group">
                    <div className="absolute -inset-0.5 bg-gradient-to-b from-slate-700 to-transparent opacity-10 rounded-2xl" />
                    <div className="relative max-h-[400px] overflow-y-auto pr-4 custom-scrollbar bg-slate-950/80 p-6 rounded-2xl border border-slate-800 shadow-inner">
                        <div className="whitespace-pre-wrap font-mono text-sm text-slate-400 leading-relaxed selection:bg-indigo-500/30">
                            {wordCount > 5 || (text && text.trim().length > 15)
                                ? text
                                : <div className="py-10 text-center">
                                    <div className="text-amber-500 font-black uppercase tracking-widest text-xs mb-2">Incomplete Scan Detected</div>
                                    <p className="text-slate-500 text-sm max-w-sm mx-auto font-medium">Wait for deep extraction or try a higher contrast image scan.</p>
                                  </div>
                            }
                        </div>
                    </div>
                </div>

                <div className="mt-8 pt-6 border-t border-slate-800/50 flex flex-wrap gap-6 items-center justify-between">
                    <div className="flex items-center gap-2 text-[9px] text-slate-600 font-black uppercase tracking-widest">
                        <Cpu className="w-3.5 h-3.5" />
                        <span>System: NewSense Neural Pipeline 2026.1</span>
                    </div>
                    {ocrConfidence !== null && (
                        <div className="flex items-center gap-3">
                            <span className="text-[9px] text-slate-500 font-black uppercase tracking-[0.2em]">Signal Strength</span>
                            <div className="w-32 h-1 bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${ocrConfidence > 0.8 ? 'bg-emerald-500' : (ocrConfidence > 0.5 ? 'bg-amber-500' : 'bg-rose-500')}`}
                                    style={{ width: `${ocrConfidence * 100}%` }}
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
