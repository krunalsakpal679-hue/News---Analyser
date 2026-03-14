import React, { useState } from 'react';
import { useAnalysisStore } from '../store/analysisStore';
import { TrendingUp, TrendingDown, Layers, ArrowRight, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export const ComparisonPage: React.FC = () => {
    const { history } = useAnalysisStore();
    const [selectedIds, setSelectedIds] = useState<string[]>([]);

    const toggleSelection = (id: string) => {
        if (selectedIds.includes(id)) {
            setSelectedIds(selectedIds.filter(idx => idx !== id));
        } else if (selectedIds.length < 5) {
            setSelectedIds([...selectedIds, id]);
        }
    };

    const selectedAnalyses = history.filter(item => selectedIds.includes(item.job_id));

    return (
        <div className="max-w-7xl mx-auto py-12 px-4 md:px-8 space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header */}
            <div className="space-y-4">
                <h1 className="text-4xl font-black text-slate-900 tracking-tight flex items-center gap-3">
                    <div className="p-3 bg-indigo-600 rounded-2xl shadow-xl shadow-indigo-200">
                        <Layers className="w-8 h-8 text-white" />
                    </div>
                    Batch Intelligence
                </h1>
                <p className="text-slate-500 text-lg max-w-2xl leading-relaxed">
                    Compare up to 5 newspaper analyses to identify trends, biases, and recurring themes across different publications or dates.
                </p>
            </div>

            {/* Selection Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Available for comparison */}
                <div className="md:col-span-1 space-y-6">
                    <div className="flex items-center justify-between px-2">
                        <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest">Select Items ({selectedIds.length}/5)</h2>
                         {selectedIds.length > 0 && (
                             <button onClick={() => setSelectedIds([])} className="text-xs font-bold text-indigo-600 hover:underline">Clear all</button>
                         )}
                    </div>
                    
                    <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                        {history.length > 0 ? (
                            history.map((item) => (
                                <div
                                    key={item.job_id}
                                    onClick={() => toggleSelection(item.job_id)}
                                    className={`
                                        p-4 rounded-2xl border-2 transition-all cursor-pointer group
                                        ${selectedIds.includes(item.job_id) 
                                            ? 'border-indigo-500 bg-indigo-50 shadow-md ring-2 ring-indigo-200' 
                                            : 'border-white bg-white hover:border-slate-200 hover:shadow-sm'}
                                    `}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3 min-w-0">
                                            <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${item.verdict === 'GOOD' ? 'bg-emerald-500' : item.verdict === 'BAD' ? 'bg-rose-500' : 'bg-slate-400'}`} />
                                            <p className="font-bold text-slate-800 text-sm truncate">{item.filename}</p>
                                        </div>
                                        {selectedIds.includes(item.job_id) && <ShieldCheck className="w-4 h-4 text-indigo-600" />}
                                    </div>
                                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-2 px-5">
                                        {new Date(item.created_at).toLocaleDateString()}
                                    </p>
                                </div>
                            ))
                        ) : (
                            <div className="p-12 text-center bg-white rounded-3xl border border-dashed border-slate-200">
                                <p className="text-slate-400 font-bold text-sm">No analysis history found</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Comparison Dashboard */}
                <div className="md:col-span-2 space-y-8">
                    {selectedAnalyses.length > 1 ? (
                        <div className="bg-white rounded-[3rem] shadow-2xl shadow-indigo-100 border border-indigo-50 p-10 space-y-12">
                            {/* Summary Stats */}
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                                <div className="p-6 bg-slate-50 rounded-3xl">
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Total Signals</p>
                                    <p className="text-3xl font-black text-slate-900">{selectedAnalyses.length}</p>
                                </div>
                                <div className="p-6 bg-emerald-50 rounded-3xl">
                                    <p className="text-[10px] font-black text-emerald-600/60 uppercase tracking-widest mb-1">Good Signals</p>
                                    <p className="text-3xl font-black text-emerald-600">{selectedAnalyses.filter(a => a.verdict === 'GOOD').length}</p>
                                </div>
                                <div className="p-6 bg-rose-50 rounded-3xl">
                                    <p className="text-[10px] font-black text-rose-600/60 uppercase tracking-widest mb-1">Bad Signals</p>
                                    <p className="text-3xl font-black text-rose-600">{selectedAnalyses.filter(a => a.verdict === 'BAD').length}</p>
                                </div>
                                <div className="p-6 bg-amber-50 rounded-3xl">
                                    <p className="text-[10px] font-black text-amber-600/60 uppercase tracking-widest mb-1">Avg Score</p>
                                    <p className="text-3xl font-black text-amber-600">
                                        {(selectedAnalyses.reduce((acc, curr) => acc + (curr.verdict_confidence || 0), 0) / selectedAnalyses.length).toFixed(2)}
                                    </p>
                                </div>
                            </div>

                            {/* Comparison list */}
                            <div className="space-y-4">
                                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest px-2">Cross-Reference View</h3>
                                <div className="space-y-4">
                                    {selectedAnalyses.map(item => (
                                        <Link 
                                            key={item.job_id} 
                                            to={`/${item.job_id}`}
                                            className="block p-8 bg-slate-50/50 hover:bg-indigo-50/50 border border-slate-100 hover:border-indigo-100 rounded-[2rem] transition-all group"
                                        >
                                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                                                <div className="space-y-2 max-w-lg">
                                                    <div className="flex items-center gap-3">
                                                        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest ${item.verdict === 'GOOD' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                                                            {item.verdict} Verdict
                                                        </span>
                                                        <span className="text-slate-400 font-bold text-xs">{new Date(item.created_at).toLocaleDateString()}</span>
                                                    </div>
                                                    <h4 className="text-xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">{item.filename}</h4>
                                                    <p className="text-slate-500 text-sm line-clamp-2 leading-relaxed">
                                                        Sentiment confidence level: {Math.round((item.verdict_confidence || 0) * 100)}%. Analysis indicates {item.verdict?.toLowerCase()} tone markers across verified extracted text.
                                                    </p>
                                                </div>
                                                <div className="flex items-center gap-6">
                                                    <div className="text-right">
                                                        <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Confidence</p>
                                                        <p className="text-2xl font-black text-slate-900">{Math.round((item.verdict_confidence || 0) * 100)}%</p>
                                                    </div>
                                                    <div className="p-4 bg-white rounded-2xl shadow-sm border border-slate-100 group-hover:bg-indigo-600 group-hover:text-white transition-all">
                                                        <ArrowRight className="w-5 h-5" />
                                                    </div>
                                                </div>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-[600px] flex flex-col items-center justify-center bg-white rounded-[4rem] border-2 border-dashed border-slate-100 p-12 text-center space-y-8">
                             <div className="relative">
                                 <div className="absolute inset-0 bg-indigo-400 blur-3xl opacity-10 animate-pulse rounded-full" />
                                 <div className="relative p-10 bg-indigo-50/50 rounded-full border border-indigo-100">
                                     <Layers className="w-16 h-16 text-indigo-400" />
                                 </div>
                             </div>
                             <div className="space-y-4 max-w-sm mx-auto">
                                 <h3 className="text-2xl font-black text-slate-800">Start Your Comparison</h3>
                                 <p className="text-slate-400 font-bold leading-relaxed">
                                     Select at least <span className="text-indigo-600">2 documents</span> from your history on the left to activate the intelligence dashboard.
                                 </p>
                             </div>
                             {selectedAnalyses.length === 1 && (
                                 <div className="flex items-center gap-2 px-6 py-3 bg-amber-50 text-amber-700 text-xs font-black uppercase tracking-widest rounded-full border border-amber-100 animate-bounce">
                                     <ArrowRight className="w-4 h-4 rotate-180" /> One more to go!
                                 </div>
                             )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
