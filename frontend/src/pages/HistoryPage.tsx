import React, { useMemo } from 'react';
import { useAnalysisStore } from '../store/analysisStore';
import { History, Search, Download, Trash2, Calendar, FileText, BarChart3, TrendingUp, TrendingDown } from 'lucide-react';
import { Link } from 'react-router-dom';

export const HistoryPage: React.FC = () => {
    const { history, setHistory } = useAnalysisStore();
    const [searchTerm, setSearchTerm] = React.useState('');

    const filteredHistory = useMemo(() => {
        return history.filter(item => 
            item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.verdict?.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [history, searchTerm]);

    const stats = useMemo(() => {
        const total = history.length;
        const good = history.filter(a => a.verdict === 'GOOD').length;
        const bad = history.filter(a => a.verdict === 'BAD').length;
        const avgConfidence = total > 0 
            ? Math.round((history.reduce((acc, curr) => acc + (curr.verdict_confidence || 0), 0) / total) * 100) 
            : 0;

        return { total, good, bad, avgConfidence };
    }, [history]);

    return (
        <div className="max-w-7xl mx-auto py-12 px-4 md:px-8 space-y-12 animate-in fade-in duration-1000">
            {/* Intel Bar */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-50 flex flex-col justify-between">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-8">Total Analyses</p>
                    <div className="flex items-end justify-between">
                        <span className="text-5xl font-black text-slate-900 leading-none">{stats.total}</span>
                        <div className="p-3 bg-indigo-50 rounded-2xl">
                            <History className="w-5 h-5 text-indigo-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-50 flex flex-col justify-between">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-8">Good/Optimistic</p>
                    <div className="flex items-end justify-between">
                        <span className="text-5xl font-black text-emerald-600 leading-none">{stats.good}</span>
                        <div className="p-3 bg-emerald-50 rounded-2xl">
                            <TrendingUp className="w-5 h-5 text-emerald-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-50 flex flex-col justify-between">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-8">Critical/Negative</p>
                    <div className="flex items-end justify-between">
                        <span className="text-5xl font-black text-rose-600 leading-none">{stats.bad}</span>
                        <div className="p-3 bg-rose-50 rounded-2xl">
                            <TrendingDown className="w-5 h-5 text-rose-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-50 flex flex-col justify-between">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-8">Avg Confidence</p>
                    <div className="flex items-end justify-between">
                        <span className="text-5xl font-black text-amber-600 leading-none">{stats.avgConfidence}%</span>
                        <div className="p-3 bg-amber-50 rounded-2xl">
                            <BarChart3 className="w-5 h-5 text-amber-600" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Main History Table */}
            <div className="bg-white rounded-[3rem] shadow-2xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
                <div className="p-10 border-b border-slate-50 flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Intelligence Ledger</h2>
                        <p className="text-slate-400 font-bold text-sm tracking-wide mt-1 uppercase tracking-[0.1em]">Archive & Trend Tracking</p>
                    </div>
                    
                    <div className="relative group">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300 group-focus-within:text-blue-600 transition-colors" />
                        <input 
                            type="text" 
                            placeholder="Search by filename or verdict..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full md:w-[350px] bg-slate-50 border-none rounded-2xl py-4 pl-12 pr-6 text-sm font-bold text-slate-800 placeholder:text-slate-300 focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-slate-50/50 border-b border-slate-50">
                                <th className="px-10 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Document</th>
                                <th className="px-10 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Date Analyzed</th>
                                <th className="px-10 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Sentiment Verdict</th>
                                <th className="px-10 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Confidence</th>
                                <th className="px-10 py-5 text-right text-[10px] font-black text-slate-400 uppercase tracking-widest">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {filteredHistory.length > 0 ? (
                                filteredHistory.map((item) => (
                                    <tr key={item.job_id} className="hover:bg-slate-50/30 transition-colors group">
                                        <td className="px-10 py-7">
                                            <div className="flex items-center gap-4">
                                                <div className="p-3 bg-slate-50 rounded-2xl group-hover:bg-white transition-colors border border-transparent group-hover:border-slate-100">
                                                    <FileText className="w-5 h-5 text-slate-400 group-hover:text-blue-600 transition-colors" />
                                                </div>
                                                <span className="font-bold text-slate-800">{item.filename}</span>
                                            </div>
                                        </td>
                                        <td className="px-10 py-7">
                                            <div className="flex items-center gap-2 text-sm text-slate-500 font-medium">
                                                <Calendar className="w-4 h-4" />
                                                {new Date(item.created_at).toLocaleDateString(undefined, {
                                                    month: 'short',
                                                    day: 'numeric',
                                                    year: 'numeric'
                                                })}
                                            </div>
                                        </td>
                                        <td className="px-10 py-7">
                                            <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm ${
                                                item.verdict === 'GOOD' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 
                                                item.verdict === 'BAD' ? 'bg-rose-50 text-rose-700 border border-rose-100' : 
                                                'bg-slate-100 text-slate-700 border border-slate-200'
                                            }`}>
                                                {item.verdict} News
                                            </span>
                                        </td>
                                        <td className="px-10 py-7">
                                           <div className="flex items-center gap-3">
                                               <div className="flex-1 h-1.5 w-24 bg-slate-100 rounded-full overflow-hidden">
                                                   <div 
                                                       className={`h-full transition-all duration-1000 ${
                                                           item.verdict === 'GOOD' ? 'bg-emerald-500' : 
                                                           item.verdict === 'BAD' ? 'bg-rose-500' : 'bg-slate-400'
                                                       }`}
                                                       style={{ width: `${Math.round((item.verdict_confidence || 0) * 100)}%` }}
                                                   />
                                               </div>
                                               <span className="font-black text-slate-900 text-xs">{Math.round((item.verdict_confidence || 0) * 100)}%</span>
                                           </div>
                                        </td>
                                        <td className="px-10 py-7 text-right">
                                            <div className="flex items-center justify-end gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Link 
                                                    to={`/${item.job_id}`}
                                                    className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl hover:bg-indigo-600 hover:text-white transition-all shadow-sm"
                                                    title="View Analysis"
                                                >
                                                    <BarChart3 className="w-4 h-4" />
                                                </Link>
                                                <button 
                                                    className="p-2.5 bg-rose-50 text-rose-600 rounded-xl hover:bg-rose-600 hover:text-white transition-all shadow-sm"
                                                    title="Delete Entry"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan={5} className="px-10 py-32 text-center">
                                        <div className="flex flex-col items-center gap-6 max-w-sm mx-auto">
                                            <div className="p-8 bg-slate-50 rounded-full border border-dashed border-slate-200">
                                                <Search className="w-12 h-12 text-slate-300" />
                                            </div>
                                            <div className="space-y-2">
                                                <h3 className="text-xl font-black text-slate-800 tracking-tight">No intelligence found</h3>
                                                <p className="text-slate-400 text-sm font-bold leading-relaxed">
                                                    Your search criteria didn't match any archived analyses. Try a different keyword or upload more documents.
                                                </p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
