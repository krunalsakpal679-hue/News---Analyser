import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || ''

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,  // 60s timeout for OCR processing
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor — add loading state
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

// Response interceptor — handle common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      throw new Error(
        'Request timed out. OCR processing may take up to 30 seconds.'
      )
    }
    if (error.response?.status === 413) {
      throw new Error('File too large. Maximum size is 50MB.')
    }
    if (error.response?.status === 422) {
      throw new Error('Invalid file type. Please upload PNG, JPG, or PDF.')
    }
    throw error
  }
)

// WebSocket — connects directly to Railway (bypasses Netlify proxy)
export function createWebSocket(
  jobId: string, 
  onMessage: (data: any) => void,
  onError?: () => void
): WebSocket {
  // Connect directly to Railway URL for WebSocket
  // Netlify cannot proxy WebSocket connections
  const wsBase = (import.meta.env.VITE_API_URL || 'ws://localhost:8000')
    .replace('https://', 'wss://')
    .replace('http://', 'ws://')
  
  const ws = new WebSocket(`${wsBase}/api/v1/ws/${jobId}`)
  
  ws.onmessage = (e) => {
    try {
      onMessage(JSON.parse(e.data))
    } catch {
      console.warn('Failed to parse WebSocket message:', e.data)
    }
  }
  
  ws.onerror = () => {
    console.warn('WebSocket error — will use polling fallback')
    onError?.()
  }
  
  return ws
}

export const documents = {
  // Upload single file
  upload: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    const res = await apiClient.post('/api/v1/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  // Upload multiple files — returns array of job results
  uploadBatch: async (files: File[]) => {
    return Promise.all(files.map(f => documents.upload(f)))
  },

  // Get job status
  getStatus: async (jobId: string) => {
    const res = await apiClient.get(`/api/v1/documents/${jobId}/status`)
    return res.data
  },

  // Get full results
  getResults: async (jobId: string) => {
    const res = await apiClient.get(`/api/v1/documents/${jobId}/results`)
    return res.data
  },

  // Poll until complete (fallback when WebSocket unavailable)
  pollUntilComplete: async (
    jobId: string,
    onProgress: (data: any) => void,
    intervalMs = 2000,
    maxAttempts = 30
  ) => {
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(r => setTimeout(r, intervalMs))
      const status = await documents.getStatus(jobId)
      onProgress(status)
      if (status.status === 'complete' || status.status === 'failed') {
        return status
      }
    }
    throw new Error('Analysis timed out after 60 seconds.')
  },
}

// Backward compatibility exports
export const uploadDocument = documents.upload;
export const getStatus = documents.getStatus;
export const getResults = documents.getResults;
export const getHistory = async (page = 1) => {
    const res = await apiClient.get('/api/v1/documents', { params: { page } });
    return res.data;
};
export const deleteJob = async (jobId: string) => {
    const res = await apiClient.get(`/api/v1/documents/${jobId}/delete`); // Adjust if needed
    return res.data;
};

export default apiClient;
