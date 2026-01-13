import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Configure axios defaults
axios.defaults.withCredentials = true

// Get CSRF token on app initialization
axios.get('/api/csrf-token/').then(response => {
  axios.defaults.headers.common['X-CSRFToken'] = response.data.csrfToken
}).catch(err => {
  console.warn('Could not get CSRF token:', err)
})

createApp(App).use(router).mount('#app')
