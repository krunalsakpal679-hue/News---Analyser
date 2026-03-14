import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Newspaper, BarChart3, History, LineChart } from 'lucide-react';
import { useAnalysisStore } from '../../store/analysisStore';

export const Navbar: React.FC = () => {
    const { history } = useAnalysisStore();
    const location = useLocation();

    // Hide navbar on processing page
    if (location.pathname.startsWith('/processing')) return null;

    return (
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200">
            <div className="max-w-7xl mx-auto px-4 md:px-8">
                <div className="flex h-20 items-center justify-between">
                    {/* Logo */}
                    <NavLink to="/" className="flex items-center gap-3 group">
                        <div className="p-2 bg-slate-900 rounded-xl group-hover:bg-blue-600 transition-colors">
                            <Newspaper className="w-6 h-6 text-white" />
                        </div>
                        <span className="text-xl font-black tracking-tighter text-slate-900">
                            NewSense <span className="text-blue-600">AI</span>
                        </span>
                    </NavLink>

                    {/* Nav Links */}
                    <div className="hidden md:flex items-center gap-1">
                        <NavLink
                            to="/"
                            className={({ isActive }) => `
                                flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all
                                ${isActive ? 'bg-slate-100 text-slate-900 shadow-inner' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'}
                            `}
                        >
                            <BarChart3 className="w-4 h-4" />
                            Direct Analysis
                        </NavLink>

                        <NavLink
                            to="/comparison"
                            className={({ isActive }) => `
                                flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all
                                ${isActive ? 'bg-slate-100 text-slate-900 shadow-inner' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'}
                            `}
                        >
                            <LineChart className="w-4 h-4" />
                            Comparison
                        </NavLink>

                        <NavLink
                            to="/history"
                            className={({ isActive }) => `
                                flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all relative
                                ${isActive ? 'bg-slate-100 text-slate-900 shadow-inner' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'}
                            `}
                        >
                            <History className="w-4 h-4" />
                            History & Trends
                            {history.length > 0 && (
                                <span className="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                            )}
                        </NavLink>
                    </div>

                    {/* Mobile nav indicator/spacer */}
                    <div className="md:hidden">
                         <div className="p-2 bg-slate-100 rounded-lg">
                             <History className="w-5 h-5 text-slate-500" />
                         </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};
