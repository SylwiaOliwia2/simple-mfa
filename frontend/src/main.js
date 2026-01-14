import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import { auth } from './utils/auth'

// Configure axios to include JWT token in requests
axios.interceptors.request.use(
  (config) => {
    const token = auth.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle 401 errors and attempt token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = auth.getRefreshToken()
        if (refreshToken) {
          const response = await axios.post('/api/token/refresh/', {
            refresh: refreshToken
          })

          const { access } = response.data
          auth.setTokens(access, refreshToken)

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`
          return axios(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        auth.clearTokens()
        router.push('/')
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

createApp(App).use(router).mount('#app')
