// src/config.ts
const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  wsUrl: (import.meta.env.VITE_API_URL || 'http://localhost:8000')
    .replace('https://', 'wss://')
    .replace('http://', 'ws://'),
  appName: import.meta.env.VITE_APP_NAME || 'NewSense AI',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
}

export default config;
