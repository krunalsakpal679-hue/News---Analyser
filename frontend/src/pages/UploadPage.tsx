// src/pages/UploadPage.tsx
import React, { useEffect } from 'react';
import { DropZone } from '../components/upload/DropZone';
import { useAnalysisStore } from '../store/analysisStore';
import { getHistory } from '../api/client';
import { Calendar, ChevronRight, Newspaper } from 'lucide-react';
import { Link } from 'react-router-dom';

export const UploadPage: React.FC = () => {
    const { history, setHistory } = useAnalysisStore();

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const data = await getHistory();
                setHistory(data.items);
            } catch (err) {
                console.error('Failed to fetch history', err);
            }
        };
        fetchHistory();
    }, [setHistory]);

    return (
        <div className="min-h-screen bg-[#f8fafc] flex flex-col items-center py-12 px-4 select-none">
            {/* Header */}
            <div className="text-center mb-12">
                <div className="inline-flex p-3 bg-blue-600 rounded-2xl shadow-xl shadow-blue-200 mb-6">
                    <Newspaper className="w-8 h-8 text-white" />
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight mb-4">
                    Analyze Your Newspaper
                </h1>
                <p className="text-slate-500 text-lg max-w-md mx-auto leading-relaxed">
                    Upload any document to instantly detect the emotional tone and sentiment of its content.
                </p>
            </div>

            {/* Main Container */}
            <div className="w-full max-w-4xl space-y-12">
                <div className="bg-white p-8 md:p-12 rounded-[2.5rem] shadow-2xl shadow-slate-200/50 border border-white">
                    <DropZone />
                </div>

                {/* History Section */}
                {history.length > 0 && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 px-2">
                            Recent Analyses
                            <span className="text-xs font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                                Past 7 days
                            </span>
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {history.map((item) => (
                                <Link
                                    key={item.job_id}
                                    to={`/${item.job_id}`}
                                    className="group bg-white p-4 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md hover:border-blue-200 transition-all flex items-center justify-between"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-3 h-3 rounded-full ${item.verdict === 'GOOD' ? 'bg-green-500' :
                                            item.verdict === 'BAD' ? 'bg-red-500' : 'bg-slate-400'
                                            }`} />
                                        <div>
                                            <h4 className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">
                                                {item.filename}
                                            </h4>
                                            <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                                                <Calendar className="w-3 h-3" />
                                                {new Date(item.created_at).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </div>
                                    <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-blue-500 transition-colors" />
                                </Link>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Footer */}
            <footer className="mt-24 text-center">
                <p className="text-slate-400 text-sm font-medium">
                    NewSense AI Pipeline · Powered by DistilBERT & VADER
                </p>
            </footer>
        </div>
    );
};
