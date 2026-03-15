import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, AlertCircle, Loader2 } from 'lucide-react';
import useAppStore from '../store/appStore';
import { useUpload } from '../hooks/useUpload';

const UploadSection: React.FC = () => {
  const { setUploadMode, uploadMode, isProcessing, error } = useAppStore();
  const { handleUpload, processingFiles } = useUpload();
  const [localFiles, setLocalFiles] = useState<File[]>([]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 5,
    onDrop: (accepted) => {
      setLocalFiles(accepted);
      if (accepted.length === 1) setUploadMode('single');
      else if (accepted.length > 1) setUploadMode('comparison');
    }
  });

  const onAnalyze = () => {
    handleUpload(localFiles);
  };

  const removeFile = (idx: number) => {
    const next = [...localFiles];
    next.splice(idx, 1);
    setLocalFiles(next);
  };

  if (isProcessing) {
    return (
      <div className="max-w-2xl mx-auto py-20 animate-in fade-in zoom-in duration-500">
        <div className="bg-white rounded-[3rem] p-12 shadow-2xl border border-slate-50 text-center space-y-10">
          <div className="relative inline-block">
            <div className="absolute inset-0 bg-indigo-500/20 blur-2xl rounded-full scale-150 animate-pulse" />
            <Loader2 className="w-16 h-16 text-indigo-600 animate-spin relative z-10" />
          </div>
          
          <div className="space-y-4">
            <h2 className="text-3xl font-black text-slate-900">Neural Intelligence Processing</h2>
            <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Synchronizing across {processingFiles.length} signal streams</p>
          </div>

          <div className="space-y-4 text-left">
            {processingFiles.map((f, i) => (
              <div key={i} className="bg-slate-50 p-6 rounded-3xl border border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-4 min-w-0">
                    <FileText className="w-5 h-5 text-indigo-400 shrink-0" />
                    <div className="truncate">
                        <p className="font-bold text-slate-800 text-sm truncate">{f.filename}</p>
                        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mt-0.5">{f.status}</p>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <p className="text-xl font-black text-slate-900">{f.progress}%</p>
                    </div>
                    <div className="w-12 h-12 rounded-full border-4 border-slate-200 border-t-indigo-600 animate-spin" style={{ animationDuration: '3s' }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-12 px-4 space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-black text-slate-900 tracking-tighter italic">NEURAL SCAN</h1>
        <p className="text-slate-400 font-bold uppercase tracking-[0.3em] text-xs">Deep Emotion Analysis & Signal Detection</p>
      </div>

      <div className="bg-white rounded-[3rem] p-4 shadow-2xl border border-white relative group">
        <div className="absolute inset-0 bg-indigo-500/5 blur-3xl rounded-[3rem] opacity-0 group-hover:opacity-100 transition-opacity" />
        
        <div
          {...getRootProps()}
          className={`
            relative min-h-[350px] border-4 border-dashed rounded-[2.5rem] transition-all flex flex-col items-center justify-center p-10 cursor-pointer
            ${isDragActive ? 'border-indigo-500 bg-indigo-50/50 scale-[1.01]' : 'border-slate-100 bg-slate-50/50 hover:bg-white hover:border-indigo-300'}
            ${localFiles.length > 0 ? 'border-emerald-200 bg-emerald-50/10' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          {localFiles.length === 0 ? (
            <div className="text-center space-y-6">
                <div className="p-8 bg-indigo-600 rounded-[2.5rem] shadow-xl shadow-indigo-200 inline-block animate-bounce">
                    <Upload className="w-10 h-10 text-white" />
                </div>
                <div className="space-y-2">
                    <h3 className="text-2xl font-black text-slate-900">Transmit Newspaper</h3>
                    <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px]">PDF · PNG · JPG (Max 5 for Comparison)</p>
                </div>
            </div>
          ) : (
            <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
              {localFiles.map((f, i) => (
                <div key={i} className="bg-white p-5 rounded-3xl shadow-sm border border-slate-100 flex items-center justify-between group/item hover:border-indigo-300 transition-colors">
                  <div className="flex items-center gap-4 truncate">
                    <div className="p-2 bg-slate-50 rounded-xl">
                        <FileText className="w-5 h-5 text-indigo-500" />
                    </div>
                    <span className="font-bold text-slate-800 text-sm truncate">{f.name}</span>
                  </div>
                  <button 
                    onClick={(e) => { e.stopPropagation(); removeFile(i); }} 
                    className="p-2 hover:bg-rose-50 hover:text-rose-500 rounded-xl transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
              {localFiles.length < 5 && (
                  <div className="flex items-center justify-center border-2 border-dashed border-slate-200 rounded-3xl p-5 text-slate-300 font-black text-xs uppercase tracking-widest">
                    Add Signal ({localFiles.length}/5)
                  </div>
              )}
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 p-6 rounded-3xl border border-rose-100 flex items-center gap-4 animate-in shake">
          <AlertCircle className="w-6 h-6 text-rose-500 shrink-0" />
          <p className="text-rose-700 font-bold text-sm tracking-tight">{error}</p>
        </div>
      )}

      {localFiles.length > 0 && !isProcessing && (
        <button
          onClick={onAnalyze}
          className="w-full py-6 bg-slate-900 hover:bg-indigo-600 text-white rounded-[2rem] font-black text-2xl shadow-2xl shadow-indigo-100 transition-all hover:scale-[1.02] active:scale-[0.98] italic"
        >
          {uploadMode === 'single' ? 'INJECT SIGNAL' : `CROSS-REFERENCE ${localFiles.length} SIGNALS`}
        </button>
      )}
    </div>
  );
};

export default UploadSection;
