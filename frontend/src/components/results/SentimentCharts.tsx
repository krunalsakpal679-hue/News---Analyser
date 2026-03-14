// src/components/results/SentimentCharts.tsx
import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { FinalScores } from '../../types/analysis';
import { AlertCircle, Activity, Heart, Scale } from 'lucide-react';

interface SentimentChartsProps {
    scores: FinalScores;
}

export const SentimentCharts: React.FC<SentimentChartsProps> = ({ scores }) => {
    const isReady = scores && (scores.positive_pct > 0 || scores.negative_pct > 0 || scores.neutral_pct > 0);
    
    const data = [
        { name: 'Positive', value: scores.positive_pct, color: '#22c55e' },
        { name: 'Negative', value: scores.negative_pct, color: '#ef4444' },
        { name: 'Neutral', value: scores.neutral_pct, color: '#94a3b8' },
    ].filter(item => item.value > 0);

    // Map compound from [-1, 1] to [0, 100] for gauge
    const gaugePercent = ((scores.compound + 1) / 2) * 100;

    const getToneDescription = () => {
        if (scores.compound > 0.6) return 'Highly Positive';
        if (scores.compound > 0.1) return 'Optimistic';
        if (scores.compound < -0.6) return 'Highly Aggressive';
        if (scores.compound < -0.1) return 'Critical / Negative';
        return 'Neutral / Balanced';
    };

    if (!isReady) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
                <div className="bg-white p-8 rounded-3xl shadow-lg border border-slate-100 flex flex-col items-center justify-center min-h-[300px]">
                    <AlertCircle className="w-10 h-10 text-slate-200 mb-4" />
                    <p className="text-slate-400 font-black uppercase tracking-widest text-[10px]">Sentiment Hub Waiting</p>
                </div>
                <div className="bg-white p-8 rounded-3xl shadow-lg border border-slate-100 flex flex-col items-center justify-center min-h-[300px]">
                    <AlertCircle className="w-10 h-10 text-slate-200 mb-4" />
                    <p className="text-slate-400 font-black uppercase tracking-widest text-[10px]">Tone Metrics Pending</p>
                </div>
                <div className="bg-white p-8 rounded-3xl shadow-lg border border-slate-100 flex flex-col items-center justify-center min-h-[300px]">
                    <AlertCircle className="w-10 h-10 text-slate-200 mb-4" />
                    <p className="text-slate-400 font-black uppercase tracking-widest text-[10px]">Emotion Logic Offline</p>
                </div>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full shrink-0">
            {/* Sentiment Score */}
            <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100 flex flex-col items-center">
                <div className="flex items-center gap-2 mb-6 self-start">
                    <div className="p-2 bg-emerald-50 rounded-xl">
                        <Activity className="w-4 h-4 text-emerald-600" />
                    </div>
                    <h3 className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px]">
                        Sentiment Score
                    </h3>
                </div>
                
                <div className="h-40 w-full relative">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                innerRadius={45}
                                outerRadius={60}
                                paddingAngle={8}
                                dataKey="value"
                                stroke="none"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ borderRadius: '15px', border: 'none', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', background: 'white' }}
                                itemStyle={{ fontWeight: '800', fontSize: '10px', textTransform: 'uppercase' }}
                                formatter={(value: any) => [`${Math.round(Number(value))}%`, '']}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                        <span className="text-3xl font-black text-slate-900 leading-none">
                            {Math.round(scores.positive_pct)}%
                        </span>
                    </div>
                </div>

                <div className="flex flex-wrap justify-center gap-3 mt-4">
                    {data.map(item => (
                        <div key={item.name} className="flex items-center gap-1.5">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">{item.name}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Tone Analysis */}
            <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100 flex flex-col">
                <div className="flex items-center gap-2 mb-10">
                    <div className="p-2 bg-indigo-50 rounded-xl">
                        <Scale className="w-4 h-4 text-indigo-600" />
                    </div>
                    <h3 className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px]">
                        Tone Analysis
                    </h3>
                </div>

                <div className="flex-1 flex flex-col justify-center px-2">
                    <div className="relative h-2.5 w-full bg-slate-50 rounded-full border border-slate-100">
                        <div className="absolute inset-0 bg-gradient-to-r from-rose-400 via-transparent to-emerald-400 opacity-20 rounded-full" />
                        <div
                            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-7 h-7 bg-white border-[7px] border-slate-900 rounded-full shadow-2xl transition-all duration-1000 ease-out z-10"
                            style={{ left: `${gaugePercent}%` }}
                        />
                    </div>

                    <div className="mt-12 text-center">
                        <div className="text-4xl font-black text-slate-900 tracking-[-0.05em] mb-2 leading-none">
                            {scores.compound > 0 ? '+' : ''}{scores.compound.toFixed(2)}
                        </div>
                        <p className="text-[11px] text-slate-500 font-black uppercase tracking-widest">{getToneDescription()}</p>
                    </div>
                </div>
            </div>

            {/* Emotion Detection */}
            <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-slate-100 flex flex-col items-center">
                 <div className="flex items-center gap-2 mb-8 self-start">
                    <div className="p-2 bg-rose-50 rounded-xl">
                        <Heart className="w-4 h-4 text-rose-600" />
                    </div>
                    <h3 className="text-slate-400 font-black uppercase tracking-[0.2em] text-[10px]">
                        Emotion Detection
                    </h3>
                </div>

                <div className="flex-1 flex flex-col items-center justify-center w-full">
                    <div className="w-24 h-24 rounded-full bg-slate-50 flex items-center justify-center border-4 border-dashed border-slate-200 mb-6">
                         <div className={`p-5 rounded-full ${scores.compound > 0.3 ? 'bg-emerald-500' : (scores.compound < -0.3 ? 'bg-rose-500' : 'bg-slate-400')} shadow-lg animate-pulse`}>
                             <Heart className="w-8 h-8 text-white fill-white" />
                         </div>
                    </div>
                    <div className="text-center">
                        <span className="text-2xl font-black text-slate-900 uppercase tracking-tight block">
                            {scores.compound > 0.4 ? 'TRUST' : (scores.compound < -0.4 ? 'CAUTION' : 'NEUTRALITY')}
                        </span>
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">Primary Emotional Signal</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
