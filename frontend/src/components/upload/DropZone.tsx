// src/components/upload/DropZone.tsx
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import { useAnalysisStore } from '../../store/analysisStore';
import { uploadDocument } from '../../api/client';
import { useNavigate } from 'react-router-dom';
import { DEMO_RESULTS } from '../../data/demoData';

export const DropZone: React.FC = () => {
    const { setFile, setJobId, uploadedFile } = useAnalysisStore();
    const [error, setError] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const navigate = useNavigate();

    const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
        if (rejectedFiles.length > 0) {
            const rej = rejectedFiles[0];
            if (rej.errors[0]?.code === 'file-too-large') {
                setError('File is too large. Max 50MB.');
            } else if (rej.errors[0]?.code === 'file-invalid-type') {
                setError('Invalid file type. Please upload PDF, PNG, or JPG.');
            } else {
                setError(rej.errors[0]?.message || 'Invalid file');
            }
            return;
        }

        if (acceptedFiles.length > 0) {
            setError(null);
            setFile(acceptedFiles[0]);
        }
    }, [setFile]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'image/png': ['.png'],
            'image/jpeg': ['.jpg', '.jpeg']
        },
        maxFiles: 1,
        maxSize: 50 * 1024 * 1024 // 50MB
    });

    const handleAnalyze = async () => {
        if (!uploadedFile) return;

        // Check for Demo Mode
        if (import.meta.env.VITE_DEMO_MODE === 'true') {
            setIsUploading(true);
            setTimeout(() => {
                let demoData;
                const filename = uploadedFile.name.toLowerCase();
                if (filename.includes('positive')) {
                    demoData = DEMO_RESULTS.positive;
                } else if (filename.includes('negative')) {
                    demoData = DEMO_RESULTS.negative;
                } else {
                    demoData = DEMO_RESULTS.neutral;
                }
                
                // We use useAnalysisStore to set results immediately in demo mode
                // and navigate straight to ResultsPage
                setJobId(demoData.job_id);
                // For demo mode, we might need to store the result in the store
                // so the ResultsPage doesn't try to fetch it from the API
                useAnalysisStore.getState().setResults(demoData as any);
                navigate(`/${demoData.job_id}`);
                setIsUploading(false);
            }, 1500);
            return;
        }

        setIsUploading(true);
        try {
            const response = await uploadDocument(uploadedFile);
            setJobId(response.job_id);
            navigate(`/processing/${response.job_id}`);
        } catch (err: any) {
            console.error('Upload error details:', err);
            
            if (err.code === 'ERR_NETWORK') {
                setError('Backend server is unreachable. Please check your internet connection or the server status.');
            } else if (err.response?.data) {
                const data = err.response.data;
                if (data.detail) {
                    const detail = data.detail;
                    if (typeof detail === 'object' && detail.errors) {
                        setError(detail.errors.join(', '));
                    } else {
                        setError(String(detail));
                    }
                } else if (data.error) {
                    setError(`${data.type || 'Error'}: ${data.error}`);
                } else {
                    setError(`Server error (${err.response.status}). Please try again.`);
                }
            } else {
                setError(err.message || 'Upload failed. Please check your connection.');
            }
        } finally {
            setIsUploading(false);
        }
    };

    const removeFile = (e: React.MouseEvent) => {
        e.stopPropagation();
        setFile(null);
        setError(null);
    };

    return (
        <div className="w-full max-w-2xl mx-auto">
            <div
                {...getRootProps()}
                className={`relative min-h-[250px] border-2 border-dashed rounded-2xl flex flex-col items-center justify-center p-8 transition-all cursor-pointer
          ${isDragActive ? 'border-blue-500 bg-blue-50/50 scale-[1.01]' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'}
          ${uploadedFile ? 'border-green-400 bg-green-50/30' : ''}
          ${error ? 'border-red-400 bg-red-50/30' : ''}
        `}
            >
                <input {...getInputProps()} />

                {!uploadedFile && !error && (
                    <>
                        <div className="p-4 bg-blue-100 rounded-full mb-4">
                            <Upload className="w-8 h-8 text-blue-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-slate-800">Drop your newspaper here</h3>
                        <p className="text-slate-500 mt-2">PDF, PNG, or JPG · Max 50MB</p>
                    </>
                )}

                {uploadedFile && !error && (
                    <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
                        <div className="p-4 bg-green-100 rounded-full mb-4">
                            <CheckCircle className="w-8 h-8 text-green-600" />
                        </div>
                        <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-lg shadow-sm border border-green-200">
                            <FileText className="w-5 h-5 text-green-600" />
                            <div className="text-left">
                                <p className="text-sm font-medium text-slate-900 truncate max-w-[200px]">{uploadedFile.name}</p>
                                <p className="text-xs text-slate-500">
                                    {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB • {uploadedFile.type.split('/')[1].toUpperCase()}
                                </p>
                            </div>
                            <button
                                onClick={removeFile}
                                className="p-1 hover:bg-slate-100 rounded-full transition-colors"
                                title="Remove file"
                            >
                                <X className="w-4 h-4 text-slate-400" />
                            </button>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="flex flex-col items-center text-center animate-in shake duration-300">
                        <div className="p-4 bg-red-100 rounded-full mb-4">
                            <AlertCircle className="w-8 h-8 text-red-600" />
                        </div>
                        <p className="text-red-600 font-medium mb-2">{error}</p>
                        <p className="text-slate-500 text-sm">Click or drag again to replace</p>
                    </div>
                )}
            </div>

            {uploadedFile && !error && (
                <button
                    onClick={handleAnalyze}
                    disabled={isUploading}
                    className={`mt-6 w-full py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold text-lg shadow-lg shadow-blue-200 transition-all flex items-center justify-center gap-2
            ${isUploading ? 'opacity-70 cursor-not-allowed' : 'active:scale-95'}`}
                >
                    {isUploading ? (
                        <>
                            <div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                            Uploading...
                        </>
                    ) : (
                        'Analyze Document'
                    )}
                </button>
            )}
        </div>
    );
};
