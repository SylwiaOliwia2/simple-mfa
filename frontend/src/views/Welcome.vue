<template>
  <div class="welcome-container">
    <div class="welcome-card">
      <h1>Success!</h1>
      <div class="actions">
        <router-link to="/mfa/setup" class="mfa-link">Setup MFA</router-link>
        <button @click="handleLogout" class="logout-button">Logout</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Welcome',
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
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100%;
}

.welcome-card {
  background: white;
  padding: 4rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  text-align: center;
}

h1 {
  color: #667eea;
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 2rem;
}

.actions {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.mfa-link {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
}

.mfa-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
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
</style>
