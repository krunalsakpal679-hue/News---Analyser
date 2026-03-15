import React from 'react';
import { Newspaper, BarChart3, History, LineChart } from 'lucide-react';
import useAppStore from '../store/appStore';

const NavBar: React.FC = () => {
    const { setSection, activeSection } = useAppStore();

    return (
        <nav className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-xl border-b border-white/5">
            <div className="max-w-7xl mx-auto px-4 md:px-8">
                <div className="flex h-20 items-center justify-between">
                    {/* Logo */}
                    <button onClick={() => setSection('upload')} className="flex items-center gap-3 group">
                        <div className="p-2 bg-indigo-600 rounded-xl group-hover:bg-white transition-all transform group-hover:rotate-12 shadow-lg shadow-indigo-500/20">
                            <Newspaper className="w-6 h-6 text-white group-hover:text-indigo-600 transition-colors" />
                        </div>
                        <span className="text-xl font-black tracking-tighter text-white">
                            NewSense <span className="text-indigo-500 uppercase italic">AI</span>
                        </span>
                    </button>

                    {/* Nav Links */}
                    <div className="flex items-center gap-1">
                        <button
                            onClick={() => setSection('upload')}
                            className={`
                                flex items-center gap-2 px-6 py-2.5 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all
                                ${activeSection === 'upload' ? 'bg-white shadow-xl text-slate-900 scale-105' : 'text-slate-400 hover:text-white hover:bg-white/5'}
                            `}
                        >
                            <BarChart3 className="w-4 h-4" />
                            <span className="hidden md:inline">Neural Scan</span>
                        </button>

                        <button
                            onClick={() => setSection('comparison')}
                            className={`
                                flex items-center gap-2 px-6 py-2.5 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all
                                ${activeSection === 'comparison' ? 'bg-white shadow-xl text-slate-900 scale-105' : 'text-slate-400 hover:text-white hover:bg-white/5'}
                            `}
                        >
                            <LineChart className="w-4 h-4" />
                            <span className="hidden md:inline">Cross-Ref</span>
                        </button>

                        <button
                            onClick={() => setSection('history')}
                            className={`
                                flex items-center gap-2 px-6 py-2.5 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all
                                ${activeSection === 'history' ? 'bg-white shadow-xl text-slate-900 scale-105' : 'text-slate-400 hover:text-white hover:bg-white/5'}
                            `}
                        >
                            <History className="w-4 h-4" />
                            <span className="hidden md:inline">History</span>
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default NavBar;
