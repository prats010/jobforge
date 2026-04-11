import axios from 'axios'

const api = axios.create({
  // Use VITE_API_URL in production, otherwise default to local proxy /api
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 120000, // 2 min timeout for AI calls
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Something went wrong'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

export default api
