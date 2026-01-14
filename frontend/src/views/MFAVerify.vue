<template>
  <div class="mfa-container">
    <div class="mfa-card">
      <h1>MFA Verification</h1>
      <p class="instruction">Enter the 6-digit code from your authenticator app</p>
      <form @submit.prevent="handleVerify">
        <div class="form-group">
          <label for="token">Verification Code</label>
          <input
            id="token"
            v-model="token"
            type="text"
            required
            placeholder="000000"
            maxlength="6"
            pattern="[0-9]{6}"
            autocomplete="one-time-code"
            @input="formatToken"
          />
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <button type="submit" :disabled="loading || token.length !== 6">
          {{ loading ? 'Verifying...' : 'Verify' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { auth } from '../utils/auth'

export default {
  name: 'MFAVerify',
  data() {
    return {
      token: '',
      error: '',
      loading: false
    }
  },
  mounted() {
    // Check if we have temp token, if not redirect to login
    const tempTokenData = auth.getTempToken()
    if (!tempTokenData.temp_token) {
      this.$router.push('/')
    }
  },
  methods: {
    formatToken(event) {
      // Only allow numbers
      this.token = event.target.value.replace(/\D/g, '').slice(0, 6)
    },
    async handleVerify() {
      if (this.token.length !== 6) {
        this.error = 'Please enter a 6-digit code'
        return
      }

      this.error = ''
      this.loading = true

      try {
        const tempTokenData = auth.getTempToken()
        
        const response = await axios.post('/api/mfa/verify/', {
          token: this.token,
          ...tempTokenData
        })

        if (response.status === 200 && response.data.access && response.data.refresh) {
          // Store JWT tokens
          auth.setTokens(response.data.access, response.data.refresh)
          // Clear only temp token data, keep JWT tokens
          localStorage.removeItem('temp_token')
          localStorage.removeItem('user_id')
          localStorage.removeItem('timestamp')
          
          this.$router.push('/welcome')
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Invalid code. Please try again.'
        this.token = ''
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.mfa-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100%;
}

.mfa-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  margin-bottom: 1rem;
  color: #333;
  font-size: 2rem;
}

.instruction {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1.5rem;
  text-align: center;
  letter-spacing: 0.5rem;
  font-family: 'Courier New', monospace;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

button {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  text-align: center;
}
</style>
