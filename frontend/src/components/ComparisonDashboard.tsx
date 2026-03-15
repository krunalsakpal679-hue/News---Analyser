import React from 'react';
import { FileText, TrendingUp, TrendingDown, Minus, Info, ArrowRight } from 'lucide-react';
import useAppStore from '../store/appStore';

interface ComparisonDashboardProps {
  results: any[];
}

const ComparisonDashboard: React.FC<ComparisonDashboardProps> = ({ results }) => {
  const { setSingleResult, setSection } = useAppStore();

  const positiveCount = results.filter(r => r.verdict === 'GOOD').length;
  const negativeCount = results.filter(r => r.verdict === 'BAD').length;
  const neutralCount = results.filter(r => r.verdict === 'NEUTRAL').length;
  const avgScore = results.reduce((sum, r) => sum + (r.final_scores?.compound || 0), 0) / (results.length || 1);

  const onViewDetail = (result: any) => {
    setSingleResult(result);
    setSection('single');
  };

  return (
    <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Summary Banner */}
      <div className="bg-slate-900 rounded-[3rem] p-10 shadow-2xl overflow-hidden relative">
         <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 blur-3xl rounded-full translate-x-32 -translate-y-32" />
         <div className="relative z-10 grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="space-y-1">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Positive Files</p>
                <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-emerald-400" />
                    <p className="text-4xl font-black text-white">{positiveCount}</p>
                </div>
            </div>
            <div className="space-y-1">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Negative Files</p>
                <div className="flex items-center gap-2">
                    <TrendingDown className="w-5 h-5 text-rose-400" />
                    <p className="text-4xl font-black text-white">{negativeCount}</p>
                </div>
            </div>
            <div className="space-y-1">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Neutral Files</p>
                <div className="flex items-center gap-2">
                    <Minus className="w-5 h-5 text-slate-400" />
                    <p className="text-4xl font-black text-white">{neutralCount}</p>
                </div>
            </div>
            <div className="space-y-1">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Avg Intelligence</p>
                <p className="text-4xl font-black text-indigo-400">{avgScore.toFixed(2)}</p>
            </div>
         </div>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {results.map((result, index) => (
          <div key={index} className="bg-white rounded-[2.5rem] border border-slate-100 shadow-xl overflow-hidden group hover:border-indigo-200 transition-all flex flex-col">
            <div className={`p-8 ${result.verdict === 'GOOD' ? 'bg-emerald-50/50' : result.verdict === 'BAD' ? 'bg-rose-50/50' : 'bg-slate-50'}`}>
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-white rounded-2xl shadow-sm">
                            <FileText className={`w-5 h-5 ${result.verdict === 'GOOD' ? 'text-emerald-500' : result.verdict === 'BAD' ? 'text-rose-500' : 'text-slate-400'}`} />
                        </div>
                        <div>
                            <h4 className="font-black text-slate-900 line-clamp-1">{result.filename || `Document ${index + 1}`}</h4>
                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Confidence: {Math.round((result.verdict_confidence || 0) * 100)}%</p>
                        </div>
                    </div>
                </div>

                <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white rounded-full border border-slate-100 shadow-sm text-[10px] font-black uppercase tracking-widest text-slate-600">
                    <Info className="w-3.5 h-3.5 text-indigo-500" />
                    {result.verdict} Signal Detected
                </div>
            </div>

            <div className="p-8 space-y-6 flex-1 flex flex-col">
                <p className="text-slate-500 text-sm leading-relaxed line-clamp-3 italic">
                    {result.explanation?.summary || 'No summary available for this scan.'}
                </p>

                <div className="space-y-3 flex-1 flex flex-col justify-end">
                    <button 
                        onClick={() => onViewDetail(result)}
                        className="w-full py-4 bg-slate-50 hover:bg-slate-900 hover:text-white text-slate-900 rounded-2xl font-black text-xs uppercase tracking-widest transition-all flex items-center justify-center gap-2 group/btn"
                    >
                        View Full Analysis
                        <ArrowRight className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                    </button>
                </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ComparisonDashboard;
