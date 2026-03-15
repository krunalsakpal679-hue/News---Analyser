import React, { useMemo, useState } from 'react';
import { History as HistoryIcon, Search, Download, Trash2, Calendar, FileText, BarChart3, TrendingUp, TrendingDown } from 'lucide-react';
import { useAnalysisStore } from '../store/analysisStore';
import useAppStore from '../store/appStore';

const HistorySection: React.FC = () => {
    const { history, setHistory } = useAnalysisStore();
    const { setSingleResult, setSection } = useAppStore();
    const [searchTerm, setSearchTerm] = useState('');

    React.useEffect(() => {
        const fetchHistory = async () => {
            try {
                const { getHistory } = await import('../api/client');
                const data = await getHistory();
                setHistory(data.items);
            } catch (err) {
                console.error('Failed to fetch history', err);
            }
        };
        fetchHistory();
    }, [setHistory]);

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

    const onViewDetail = (item: any) => {
        // In a real app we'd fetch the full result here if not in history
        // but for now we'll assume history has enough or use jobId to fetch in Results view
        setSingleResult(item); 
        setSection('single');
    };

    return (
        <div className="space-y-12 animate-in fade-in duration-700">
            {/* Intel Bar */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-slate-50 flex flex-col justify-between">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-8">Total Analyses</p>
                    <div className="flex items-end justify-between">
                        <span className="text-5xl font-black text-slate-900 leading-none">{stats.total}</span>
                        <div className="p-3 bg-indigo-50 rounded-2xl">
                            <HistoryIcon className="w-5 h-5 text-indigo-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-slate-50 flex flex-col justify-between">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-8">Good Signals</p>
                    <div className="flex items-end justify-between">
                        <span className="text-5xl font-black text-emerald-600 leading-none">{stats.good}</span>
                        <div className="p-3 bg-emerald-50 rounded-2xl">
                            <TrendingUp className="w-5 h-5 text-emerald-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-slate-50 flex flex-col justify-between">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-8">Bad Signals</p>
                    <div className="flex items-end justify-between">
                        <span className="text-5xl font-black text-rose-600 leading-none">{stats.bad}</span>
                        <div className="p-3 bg-rose-50 rounded-2xl">
                            <TrendingDown className="w-5 h-5 text-rose-600" />
                        </div>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-slate-50 flex flex-col justify-between">
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
            <div className="bg-white rounded-[3rem] shadow-2xl border border-slate-100 overflow-hidden">
                <div className="p-10 border-b border-slate-50 flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Intelligence Ledger</h2>
                        <p className="text-slate-400 font-bold text-sm tracking-wide mt-1 uppercase tracking-[0.1em]">Archive & Trend Tracking</p>
                    </div>
                    <div className="relative group">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300 group-focus-within:text-blue-600 transition-colors" />
                        <input 
                            type="text" 
                            placeholder="Find analysis..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full md:w-[350px] bg-slate-50 border-none rounded-2xl py-4 pl-12 pr-6 text-sm font-bold text-slate-800 focus:ring-2 focus:ring-blue-100 transition-all"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-slate-50/50 border-b border-slate-50">
                                <th className="px-10 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Document</th>
                                <th className="px-10 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Date</th>
                                <th className="px-10 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Verdict</th>
                                <th className="px-10 py-5 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">Confidence</th>
                                <th className="px-10 py-5 text-right text-[10px] font-black text-slate-400 uppercase tracking-widest">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {filteredHistory.map((item) => (
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
                                        <span className="text-sm text-slate-500 font-medium">{new Date(item.created_at).toLocaleDateString()}</span>
                                    </td>
                                    <td className="px-10 py-7">
                                        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm ${
                                            item.verdict === 'GOOD' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 
                                            item.verdict === 'BAD' ? 'bg-rose-50 text-rose-700 border border-rose-100' : 
                                            'bg-slate-100 text-slate-700 border border-slate-200'
                                        }`}>
                                            {item.verdict}
                                        </span>
                                    </td>
                                    <td className="px-10 py-7 font-black text-slate-900 text-xs">
                                        {Math.round((item.verdict_confidence || 0) * 100)}%
                                    </td>
                                    <td className="px-10 py-7 text-right">
                                        <button 
                                            onClick={() => onViewDetail(item)}
                                            className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl hover:bg-indigo-600 hover:text-white transition-all shadow-sm"
                                        >
                                            <BarChart3 className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default HistorySection;
