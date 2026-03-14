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
                    const { status } = useAnalysisStore.getState();
                    if (status !== 'complete' && status !== 'failed' && reconnectCount.current < maxReconnects) {
                        reconnectCount.current += 1;
                    }
                }
            );
            
            socketRef.current = socket;
        };

        connect();

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
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
