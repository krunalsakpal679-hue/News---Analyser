import { useState } from 'react'
import useAppStore from '../store/appStore'
import * as api from '../api/client'

export function useUpload() {
  const {
    setSection,
    setProcessing,
    setSingleResult,
    addBatchResult,
    clearBatchResults,
    setError,
    uploadMode,
  } = useAppStore()

  const [processingFiles, setProcessingFiles] = useState<{ filename: string; status: string; progress: number }[]>([])

  const pollUntilComplete = async (
    jobId: string,
    filename: string,
    index: number
  ) => {
    const maxAttempts = 30
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(r => setTimeout(r, 2000))
      
      const status = await api.getStatus(jobId)
      
      setProcessingFiles(prev => prev.map((f, idx) =>
        idx === index
          ? { ...f, status: status.status, progress: status.progress_pct || 0 }
          : f
      ))
      
      if (status.status === 'complete') {
        const result = await api.getResults(jobId)
        return result
      }
      
      if (status.status === 'failed') {
        throw new Error(`Analysis failed for ${filename}`)
      }
    }
    throw new Error(`Timeout waiting for ${filename}`)
  }

  const handleUpload = async (files: File[]) => {
    setError(null)
    setProcessing(true)
    clearBatchResults()

    // Initialise processing state for all files
    setProcessingFiles(files.map(f => ({
      filename: f.name,
      status: 'uploading',
      progress: 0,
    })))

    try {
      if (files.length === 1) {
        // ── SINGLE MODE ──────────────────────────────────────
        const { job_id } = await api.uploadDocument(files[0])
        
        setProcessingFiles([{
          filename: files[0].name,
          status: 'processing',
          progress: 10,
        }])

        const result = await pollUntilComplete(job_id, files[0].name, 0)
        
        setSingleResult(result)
        setSection('single')   // ← go to single dashboard

      } else {
        // ── COMPARISON MODE ──────────────────────────────────
        // Upload all files simultaneously
        const uploadPromises = files.map(async (file, index) => {
          const { job_id } = await api.uploadDocument(file)
          
          setProcessingFiles(prev => prev.map((f, i) =>
            i === index ? { ...f, status: 'processing', progress: 5 } : f
          ))
          
          return { job_id, filename: file.name, index }
        })

        const uploadedJobs = await Promise.all(uploadPromises)

        // Poll all jobs simultaneously
        const resultPromises = uploadedJobs.map(({ job_id, filename, index }) =>
          pollUntilComplete(job_id, filename, index)
        )

        const allResults = await Promise.all(resultPromises)

        // Add all results to batch store
        allResults.forEach(result => addBatchResult(result))

        // ── THIS IS THE KEY LINE ──
        setSection('comparison')  // ← go to comparison dashboard
      }

    } catch (err: any) {
      setError(err.message || 'Upload failed. Please try again.')
    } finally {
      setProcessing(false)
    }
  }

  return { handleUpload, processingFiles }
}
