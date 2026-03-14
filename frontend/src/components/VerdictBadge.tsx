import React from 'react';
import { CheckCircle, XCircle, MinusCircle } from 'lucide-react';

interface VerdictBadgeProps {
    verdict: 'GOOD' | 'BAD' | 'NEUTRAL' | string | null;
    confidence?: number;
}

const VerdictBadge: React.FC<VerdictBadgeProps> = ({ verdict, confidence }) => {
    if (!verdict) return null;

    const config = {
        GOOD: {
            bg: 'bg-success-50/10',
            text: 'text-emerald-400',
            border: 'border-emerald-500/30',
            shadow: 'shadow-emerald-500/20',
            label: 'Positive',
            Icon: CheckCircle
        },
        BAD: {
            bg: 'bg-danger-50/10',
            text: 'text-red-400',
            border: 'border-red-500/30',
            shadow: 'shadow-red-500/20',
            label: 'Critical',
            Icon: XCircle
        },
        NEUTRAL: {
            bg: 'bg-gray-50/10',
            text: 'text-gray-400',
            border: 'border-gray-500/30',
            shadow: 'shadow-gray-500/20',
            label: 'Balanced',
            Icon: MinusCircle
        }
    }[verdict as keyof typeof config] || {
        bg: 'bg-gray-50/10',
        text: 'text-gray-400',
        border: 'border-gray-500/30',
        shadow: 'shadow-gray-500/20',
        label: verdict,
        Icon: MinusCircle
    };

    const { bg, text, border, shadow, label, Icon } = config;

    return (
        <div className={`
      relative h-32 w-full max-w-md mx-auto 
      flex flex-col items-center justify-center 
      rounded-3xl border-2 ${border} ${bg} ${text} 
      shadow-2xl ${shadow} glass verdict-pulse transition-all duration-500
    `}>
            <Icon className="w-12 h-12 mb-2" strokeWidth={1.5} />
            <span className="text-4xl font-black tracking-tighter uppercase">{label}</span>
            {confidence !== undefined && (
                <div className="absolute bottom-3 text-xs font-medium opacity-60 uppercase tracking-widest">
                    Confidence: {(confidence * 100).toFixed(1)}%
                </div>
            )}
        </div>
    );
};

export default VerdictBadge;
