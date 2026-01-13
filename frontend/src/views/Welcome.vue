<template>
  <div class="welcome-container">
    <div class="welcome-card">
      <h1>Success!</h1>
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
}
</style>
