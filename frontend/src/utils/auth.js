// JWT token management utilities

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const TEMP_TOKEN_KEY = 'temp_token'
const USER_ID_KEY = 'user_id'
const TIMESTAMP_KEY = 'timestamp'

export const auth = {
  // Store JWT tokens
  setTokens(accessToken, refreshToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  },

  // Get access token
  getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  },

  // Get refresh token
  getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },

  // Store temporary token for MFA flow
  setTempToken(tempToken, userId, timestamp) {
    localStorage.setItem(TEMP_TOKEN_KEY, tempToken)
    localStorage.setItem(USER_ID_KEY, userId)
    localStorage.setItem(TIMESTAMP_KEY, timestamp)
  },

  // Get temporary token data
  getTempToken() {
    return {
      temp_token: localStorage.getItem(TEMP_TOKEN_KEY),
      user_id: localStorage.getItem(USER_ID_KEY),
      timestamp: localStorage.getItem(TIMESTAMP_KEY)
    }
  },

  // Clear all tokens
  clearTokens() {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(TEMP_TOKEN_KEY)
    localStorage.removeItem(USER_ID_KEY)
    localStorage.removeItem(TIMESTAMP_KEY)
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getAccessToken()
  }
}
