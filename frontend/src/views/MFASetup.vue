<template>
  <div class="mfa-setup-container">
    <div class="mfa-setup-card">
      <h1>Setup MFA</h1>
      <div v-if="setupRequired && qrCode" class="setup-content">
        <p class="instruction">
          MFA setup is required. Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
        </p>
        <div class="qr-code-container">
          <img :src="qrCode" alt="MFA QR Code" class="qr-code" />
        </div>
        <p class="secret-info">
          Or enter this secret manually: <code>{{ secret }}</code>
        </p>
        <div class="form-group">
          <label for="token">Enter verification code to confirm setup</label>
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
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
        <button type="button" @click="handleConfirm" :disabled="loading || token.length !== 6">
          {{ loading ? 'Confirming...' : 'Confirm Setup' }}
        </button>
      </div>
      <div v-else-if="!setupRequired" class="already-setup">
        <p>MFA is already set up for your account.</p>
        <button type="button" @click="goToWelcome">Go to Welcome Page</button>
      </div>
      <div v-else class="loading">
        <p>Loading setup information...</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { auth } from '../utils/auth'

export default {
  name: 'MFASetup',
  data() {
    return {
      qrCode: null,
      secret: null,
      token: '',
      error: '',
      success: '',
      loading: false,
      setupRequired: true
    }
  },
  async mounted() {
    // Check if we have temp token, if not redirect to login
    const tempTokenData = auth.getTempToken()
    if (!tempTokenData.temp_token) {
      this.$router.push('/')
      return
    }
    await this.loadSetup()
  },
  methods: {
    formatToken(event) {
      // Only allow numbers
      this.token = event.target.value.replace(/\D/g, '').slice(0, 6)
    },
    async loadSetup() {
      try {
        const tempTokenData = auth.getTempToken()
        
        const response = await axios.get('/api/mfa/setup/', {
          params: tempTokenData
        })
        
        if (response.data.setup_required) {
          this.qrCode = response.data.qr_code
          this.secret = response.data.secret
          this.setupRequired = true
        } else {
          this.setupRequired = false
        }
      } catch (err) {
        this.error = 'Failed to load MFA setup. Please try again.'
        console.error(err)
      }
    },
    async handleConfirm() {
      if (this.token.length !== 6) {
        this.error = 'Please enter a 6-digit code'
        return
      }

      this.error = ''
      this.success = ''
      this.loading = true

      try {
        const tempTokenData = auth.getTempToken()
        
        const response = await axios.post('/api/mfa/confirm/', {
          token: this.token,
          ...tempTokenData
        })

        if (response.status === 200 && response.data.access && response.data.refresh) {
          // Store JWT tokens
          auth.setTokens(response.data.access, response.data.refresh)
          // Clear temp token
          localStorage.removeItem('temp_token')
          localStorage.removeItem('user_id')
          localStorage.removeItem('timestamp')
          
          this.success = 'MFA setup confirmed successfully!'
          // Redirect to welcome page after a short delay
          setTimeout(() => {
            this.$router.push('/welcome')
          }, 1500)
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Invalid code. Please try again.'
        this.token = ''
      } finally {
        this.loading = false
      }
    },
    goToWelcome() {
      this.$router.push('/welcome')
    }
  }
}
</script>

<style scoped>
.mfa-setup-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100%;
}

.mfa-setup-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 500px;
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
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.qr-code-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.qr-code {
  width: 250px;
  height: 250px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  background: white;
}

.secret-info {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #666;
  font-size: 0.9rem;
}

.secret-info code {
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  word-break: break-all;
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

.success-message {
  background: #efe;
  color: #3c3;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  text-align: center;
}

.already-setup {
  text-align: center;
}

.already-setup p {
  margin-bottom: 1.5rem;
  color: #666;
}

.loading {
  text-align: center;
  color: #666;
}
</style>
