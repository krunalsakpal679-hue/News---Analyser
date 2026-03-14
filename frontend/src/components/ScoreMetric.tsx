import React from 'react';

interface ScoreMetricProps {
    label: string;
    value: number;
    type?: 'percentage' | 'score';
    color?: string;
}

const ScoreMetric: React.FC<ScoreMetricProps> = ({ label, value, type = 'score', color = 'text-white' }) => {
    const displayValue = type === 'percentage' ? `${value}%` : value.toFixed(2);

    return (
        <div className="flex flex-col p-4 rounded-2xl bg-white/5 border border-white/10">
            <span className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">{label}</span>
            <span className={`text-2xl font-mono font-bold ${color}`}>{displayValue}</span>

            {type === 'percentage' && (
                <div className="mt-2 h-1 w-full bg-white/10 rounded-full overflow-hidden">
                    <div
                        className={`h-full ${color.replace('text-', 'bg-')}`}
                        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
                    />
                </div>
            )}
        </div>
    );
};

export default ScoreMetric;
