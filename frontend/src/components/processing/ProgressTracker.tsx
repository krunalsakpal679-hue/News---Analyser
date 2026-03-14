// src/components/processing/ProgressTracker.tsx
import React from 'react';
import { Check, Loader2, Circle } from 'lucide-react';
import { AnalysisStatus } from '../../types/analysis';

interface Step {
    id: AnalysisStatus;
    label: string;
}

const STEPS: Step[] = [
    { id: 'queued', label: 'Waiting in queue' },
    { id: 'extracting', label: 'Reading document text' },
    { id: 'cleaning', label: 'Cleaning and preparing text' },
    { id: 'analyzing', label: 'Analyzing sentiment' },
    { id: 'complete', label: 'Finalizing results' },
];

interface ProgressTrackerProps {
    currentStatus: AnalysisStatus;
    progressPct: number;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({ currentStatus, progressPct }) => {
    const currentStepIndex = STEPS.findIndex(s => s.id === currentStatus);

    return (
        <div className="w-full max-w-md mx-auto p-6 bg-white rounded-2xl shadow-xl border border-slate-100">
            <div className="mb-8">
                <div className="flex justify-between items-end mb-2">
                    <h3 className="font-bold text-slate-800 text-lg">Processing...</h3>
                    <span className="text-blue-600 font-mono font-bold text-xl">{Math.round(progressPct)}%</span>
                </div>
                <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200">
                    <div
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500 ease-out shadow-[0_0_10px_rgba(59,130,246,0.3)]"
                        style={{ width: `${progressPct}%` }}
                    />
                </div>
                <p className="text-slate-400 text-xs mt-3 text-center">Estimated time: 10–30 seconds</p>
            </div>

            <div className="space-y-6 relative">
                {/* Connector Line */}
                <div className="absolute left-[15px] top-2 bottom-2 w-0.5 bg-slate-100" />

                {STEPS.map((step, index) => {
                    const isCompleted = index < currentStepIndex || currentStatus === 'complete';
                    const isCurrent = index === currentStepIndex && currentStatus !== 'complete';

                    return (
                        <div key={step.id} className="flex items-center gap-4 relative z-10">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${isCompleted ? 'bg-green-500 text-white shadow-md' :
                                    isCurrent ? 'bg-blue-600 text-white ring-4 ring-blue-100 animate-pulse shadow-lg' :
                                        'bg-white border-2 border-slate-200 text-slate-300'
                                }`}>
                                {isCompleted ? (
                                    <Check className="w-5 h-5" />
                                ) : isCurrent ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <Circle className="w-4 h-4" />
                                )}
                            </div>
                            <div className="flex flex-col">
                                <span className={`font-medium transition-colors ${isCompleted ? 'text-slate-900 line-through decoration-slate-300' :
                                        isCurrent ? 'text-blue-600 font-bold' :
                                            'text-slate-400'
                                    }`}>
                                    {step.label}
                                </span>
                                {isCurrent && (
                                    <span className="text-[10px] text-blue-400 uppercase tracking-widest font-bold animate-pulse">
                                        Active
                                    </span>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
