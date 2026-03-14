// src/hooks/useJobProgress.ts
import { useEffect, useState, useRef } from 'react';
import { useAnalysisStore } from '../store/analysisStore';
import { createWebSocket } from '../api/client';

const STAGE_LABELS: Record<string, string> = {
    extracting: 'Reading document...',
    cleaning: 'Processing text...',
    analyzing: 'Analyzing sentiment...',
    complete: 'Analysis complete!',
    failed: 'Analysis failed',
    queued: 'Waiting in queue...',
};

export const useJobProgress = (jobId: string | null) => {
    const { updateProgress, setResults } = useAnalysisStore();
    const [errorMsg, setErrorMsg] = useState<string | null>(null);
    const reconnectCount = useRef(0);
    const maxReconnects = 10;
    const socketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!jobId) return;

        let pollingInterval: any = null;

        const startPolling = () => {
             if (pollingInterval) return;
             console.log('Starting polling fallback...');
             pollingInterval = setInterval(async () => {
                 try {
                     const { getStatus, getResults } = await import('../api/client');
                     const data = await getStatus(jobId);
                     const backendEvent = data.status;
                     const progressValue = data.progress_pct || 0;

                     updateProgress(backendEvent as any, progressValue);

                     if (backendEvent === 'complete') {
                         const resultsData = await getResults(jobId);
                         setResults(resultsData);
                         clearInterval(pollingInterval);
                     } else if (backendEvent === 'failed') {
                         setErrorMsg(data.error_message || 'Analysis failed');
                         clearInterval(pollingInterval);
                     }
                 } catch (err) {
                     console.error('Polling error:', err);
                 }
             }, 2000);
        };

        const connect = () => {
            const socket = createWebSocket(
                jobId, 
                (data) => {
                    const backendEvent = data.event || data.status;
                    const progressValue = data.progress !== undefined ? data.progress : data.progress_pct || 0;

                    if (backendEvent) {
                        if (backendEvent !== 'failed' && backendEvent !== 'error') {
                            setErrorMsg(null);
                        }

                        updateProgress(backendEvent as any, progressValue);

                        if (backendEvent === 'complete' && data.results) {
                            setResults(data.results);
                        }

                        if (backendEvent === 'failed' || backendEvent === 'error') {
                            setErrorMsg(data.error || data.message || 'Analysis failed');
                        }
                    }
                },
                () => {
                    console.warn('Socket error in hook — jumping to polling');
                    startPolling();
                }
            );
            
            socketRef.current = socket;
        };

        connect();

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
            }
            if (pollingInterval) {
                clearInterval(pollingInterval);
            }
        };
    }, [jobId, updateProgress, setResults]);

    const { status, progressPct } = useAnalysisStore();

    return {
        status,
        progressPct,
        currentStage: status ? STAGE_LABELS[status] || status : 'Initializing...',
        isComplete: status === 'complete',
        hasError: status === 'failed' || !!errorMsg,
        errorMsg,
    };
};
