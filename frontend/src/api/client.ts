import axios from 'axios'
import config from '../config'

const BASE_URL = config.apiUrl

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
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
    // Just pass the error through for specific components to handle
    return Promise.reject(error)
  }
)

// WebSocket — connects directly to Railway (bypasses Netlify proxy)
export function createWebSocket(
  jobId: string, 
  onMessage: (data: any) => void,
  onError?: () => void
): WebSocket {
  const wsBase = config.wsUrl
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
