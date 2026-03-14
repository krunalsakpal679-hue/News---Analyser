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
