// src/components/results/MetadataStrip.tsx
import React from 'react';
import { Clock, Globe, Hash, AlertTriangle } from 'lucide-react';

interface MetadataStripProps {
    wordCount: number;
    language: string;
    duration: number; // in seconds
    warnings: string[];
}

export const MetadataStrip: React.FC<MetadataStripProps> = ({ wordCount, language, duration, warnings }) => {
    return (
        <div className="w-full flex flex-col gap-4">
            <div className="flex flex-wrap items-center justify-center gap-6 py-4 px-8 bg-slate-50 rounded-2xl border border-slate-100 italic text-slate-500 text-sm">
                <div className="flex items-center gap-2">
                    <Hash className="w-4 h-4" />
                    <span>{wordCount.toLocaleString()} words analyzed</span>
                </div>
                <div className="w-1.5 h-1.5 rounded-full bg-slate-200" />
                <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4" />
                    <span>Language: {language}</span>
                </div>
                <div className="w-1.5 h-1.5 rounded-full bg-slate-200" />
                <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>Analyzed in {duration.toFixed(1)}s</span>
                </div>
            </div>

            {warnings.length > 0 && (
                <div className="flex flex-wrap gap-2 animate-in fade-in slide-in-from-bottom duration-500">
                    {warnings.map((warning, idx) => (
                        <div
                            key={idx}
                            className="flex items-center gap-2 px-3 py-1.5 bg-yellow-50 text-yellow-700 text-[10px] font-bold uppercase tracking-wider rounded-lg border border-yellow-200 shadow-sm"
                        >
                            <AlertTriangle className="w-3.5 h-3.5" />
                            {warning}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
