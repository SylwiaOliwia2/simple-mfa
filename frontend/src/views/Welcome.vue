<template>
  <div class="welcome-container">
    <nav class="navbar">
      <div class="nav-content">
        <h2 class="nav-title">Navigation</h2>
        <div class="nav-buttons">
          <button @click="showLuckyNumber" class="nav-button">Lucky Number</button>
          <button @click="showQuote" class="nav-button">Quote of the day</button>
          <button @click="handleLogout" class="logout-button">Logout</button>
        </div>
      </div>
    </nav>
    
    <div class="main-content">
      <h1 class="greeting">Hello</h1>
      
      <div class="content-area">
        <div v-if="currentView === 'lucky'" class="result-card">
          <h2>Your Lucky Number</h2>
          <div v-if="luckyNumber" class="lucky-number">{{ luckyNumber }}</div>
          <div v-else class="loading">Generating...</div>
        </div>
        
        <div v-else-if="currentView === 'quote'" class="result-card">
          <h2>Quote of the Day</h2>
          <div v-if="quote" class="quote-text">{{ quote }}</div>
          <div v-else class="loading">Loading quote...</div>
        </div>
        
        <div v-else class="welcome-message">
          <p>Welcome! Use the navigation bar to explore features.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Welcome',
  data() {
    return {
      currentView: null,
      luckyNumber: null,
      quote: null,
      loading: false
    }
  },
  async mounted() {
    // Verify authentication on mount
    try {
      axios.defaults.withCredentials = true
      await axios.get('/api/welcome/')
    } catch (err) {
      // If not authenticated, redirect to login
      this.$router.push('/')
    }
  },
  methods: {
    async showLuckyNumber() {
      this.currentView = 'lucky'
      this.luckyNumber = null
      this.loading = true
      
      try {
        axios.defaults.withCredentials = true
        const response = await axios.get('/api/lucky-number/')
        this.luckyNumber = response.data.number
      } catch (err) {
        console.error('Error fetching lucky number:', err)
        this.luckyNumber = 'Error loading number'
      } finally {
        this.loading = false
      }
    },
    async showQuote() {
      this.currentView = 'quote'
      this.quote = null
      this.loading = true
      
      try {
        axios.defaults.withCredentials = true
        const response = await axios.get('/api/quote-of-the-day/')
        this.quote = response.data.quote
      } catch (err) {
        console.error('Error fetching quote:', err)
        this.quote = 'Error loading quote'
      } finally {
        this.loading = false
      }
    },
    async handleLogout() {
      try {
        axios.defaults.withCredentials = true
        await axios.post('/api/logout/')
        // Redirect to login page after successful logout
        this.$router.push('/')
      } catch (err) {
        // Even if there's an error, redirect to login
        console.error('Logout error:', err)
        this.$router.push('/')
      }
    }
  }
}
</script>

<style scoped>
.welcome-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.nav-title {
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.nav-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-button {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}

.nav-button:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.logout-button {
  padding: 0.75rem 1.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}

.logout-button:hover {
  background: #c82333;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(220, 53, 69, 0.4);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 3rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.greeting {
  color: #667eea;
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 3rem;
  text-align: center;
}

.content-area {
  width: 100%;
  max-width: 800px;
}

.result-card {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-card h2 {
  color: #333;
  font-size: 2rem;
  margin-bottom: 2rem;
  font-weight: 600;
}

.lucky-number {
  font-size: 5rem;
  font-weight: 700;
  color: #667eea;
  margin: 2rem 0;
  text-shadow: 2px 2px 4px rgba(102, 126, 234, 0.2);
}

.quote-text {
  font-size: 1.5rem;
  color: #555;
  line-height: 1.8;
  font-style: italic;
  padding: 2rem;
  border-left: 4px solid #667eea;
  background: #f9f9f9;
  border-radius: 6px;
}

.loading {
  font-size: 1.2rem;
  color: #999;
  padding: 2rem;
}

.welcome-message {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.welcome-message p {
  font-size: 1.2rem;
  color: #666;
  margin: 0;
}

@media (max-width: 768px) {
  .nav-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .nav-buttons {
    width: 100%;
  }
  
  .nav-button,
  .logout-button {
    flex: 1;
    min-width: 120px;
  }
  
  .greeting {
    font-size: 3rem;
  }
  
  .lucky-number {
    font-size: 4rem;
  }
  
  .quote-text {
    font-size: 1.2rem;
  }
}
</style>
