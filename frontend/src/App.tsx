import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { UploadPage } from './pages/UploadPage';
import { ProcessingPage } from './pages/ProcessingPage';
import { ResultsPage } from './pages/ResultsPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { HistoryPage } from './pages/HistoryPage';
import { Navbar } from './components/layout/Navbar';

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-slate-50 font-sans antialiased text-slate-900">
                <Navbar />
                <Routes>
                    <Route path="/" element={<UploadPage />} />
                    <Route path="/comparison" element={<ComparisonPage />} />
                    <Route path="/history" element={<HistoryPage />} />
                    <Route path="/processing/:jobId" element={<ProcessingPage />} />
                    <Route path="/:jobId" element={<ResultsPage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
