// src/pages/ProcessingPage.tsx
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useJobProgress } from '../hooks/useJobProgress';
import { ProgressTracker } from '../components/processing/ProgressTracker';
import { XCircle, ArrowLeft } from 'lucide-react';
import { deleteJob } from '../api/client';

export const ProcessingPage: React.FC = () => {
    const { jobId } = useParams<{ jobId: string }>();
    const navigate = useNavigate();
    const { status, progressPct, currentStage, isComplete, hasError, errorMsg } = useJobProgress(jobId || null);

    useEffect(() => {
        if (isComplete) {
            navigate(`/${jobId}`);
        }
    }, [isComplete, jobId, navigate]);

    const handleCancel = async () => {
        if (jobId) {
            try {
                await deleteJob(jobId);
            } finally {
                navigate('/');
            }
        }
    };

    // Only show failure UI if the backend explicitly failed or if we have a persistent error message
    // without being in a 'complete' state.
    const isActuallyFailed = status === 'failed' || (errorMsg && status !== 'complete' && !currentStage.includes('Retrying'));

    if (isActuallyFailed) {
        return (
            <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 text-center">
                <div className="p-6 bg-red-50 rounded-full mb-6">
                    <XCircle className="w-16 h-16 text-red-500" />
                </div>
                <h1 className="text-3xl font-black text-slate-900 mb-2">Analysis Failed</h1>
                <p className="text-slate-500 mb-8 max-w-md">{errorMsg || 'Something went wrong during the pipeline run.'}</p>
                <button
                    onClick={() => navigate('/')}
                    className="px-8 py-3 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 transition-all flex items-center gap-2"
                >
                    <ArrowLeft className="w-5 h-5" />
                    Back to Upload
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]">
            <div className="w-full max-w-lg">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-black text-slate-900 mb-2">Analyzing Document</h2>
                    <p className="text-slate-500 font-medium">{currentStage}</p>
                </div>

                <ProgressTracker currentStatus={status || 'queued'} progressPct={progressPct} />

                <div className="mt-12 flex justify-center">
                    <button
                        onClick={handleCancel}
                        className="text-slate-400 hover:text-red-500 font-bold text-sm transition-colors uppercase tracking-widest px-6 py-2 border border-slate-200 rounded-full hover:border-red-100"
                    >
                        Cancel Analysis
                    </button>
                </div>
            </div>
        </div>
    );
};
