import { useEffect } from 'react'
import useAppStore from './store/appStore'
import { useAnalysisStore } from './store/analysisStore'
import NavBar from './components/NavBar'
import UploadSection from './components/UploadSection'
import SingleDashboard from './components/SingleDashboard'
import ComparisonDashboard from './components/ComparisonDashboard'
import HistorySection from './components/HistorySection'

function App() {
  const { activeSection, singleResult, batchResults, setSection, reset } = useAppStore()
  const { setHistory, history } = useAnalysisStore()

  // Save to history logic
  useEffect(() => {
    if (singleResult) {
       const existing = history.find(h => h.job_id === singleResult.job_id);
       if (!existing) {
         const newHistory = [singleResult, ...history].slice(0, 50);
         setHistory(newHistory as any);
         localStorage.setItem('newsense_history', JSON.stringify(newHistory));
       }
    }
  }, [singleResult]);

  useEffect(() => {
    if (batchResults.length > 0) {
      const newItems = batchResults.filter(br => !history.find(h => h.job_id === br.job_id));
      if (newItems.length > 0) {
        const newHistory = [...newItems, ...history].slice(0, 50);
        setHistory(newHistory as any);
        localStorage.setItem('newsense_history', JSON.stringify(newHistory));
      }
    }
  }, [batchResults]);

  // Fallback logic
  useEffect(() => {
    if (activeSection === 'single' && !singleResult) {
      setSection('upload');
    }
    if (activeSection === 'comparison' && batchResults.length === 0) {
      setSection('upload');
    }
  }, [activeSection, singleResult, batchResults, setSection]);

  return (
    <div className="min-h-screen bg-[#0A0F1E] text-slate-200 selection:bg-indigo-500/30">
      <NavBar />
      
      <main className="max-w-7xl mx-auto py-12 px-4">
        {activeSection === 'upload' && (
          <UploadSection />
        )}
        
        {activeSection === 'single' && singleResult && (
          <SingleDashboard result={singleResult} />
        )}
        
        {activeSection === 'comparison' && batchResults.length > 0 && (
          <ComparisonDashboard results={batchResults} />
        )}
        
        {activeSection === 'history' && (
          <HistorySection />
        )}
      </main>

      {/* Global Reset/New Scan for ease of use */}
      {(activeSection !== 'upload') && (
        <button 
          onClick={reset}
          className="fixed bottom-10 right-10 bg-indigo-600 hover:bg-white hover:text-indigo-600 text-white p-5 rounded-full shadow-2xl shadow-indigo-500/20 transition-all hover:rotate-90 group z-50"
        >
           <span className="sr-only">New Scan</span>
           <div className="text-xl font-black">+</div>
        </button>
      )}
    </div>
  )
}

export default App
