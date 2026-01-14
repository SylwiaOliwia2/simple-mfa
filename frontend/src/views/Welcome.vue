<template>
  <div class="welcome-container">
    <nav class="navbar">
      <div class="nav-content">
        <h2 class="nav-title">Navigation</h2>
        <div class="nav-buttons">
          <button @click="showLuckyNumber" class="nav-button">Lucky Number</button>
          <button @click="showQuote" class="nav-button">Quote of the day</button>
          <button @click="showNotes" class="nav-button">My notes</button>
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
        
        <div v-else-if="currentView === 'notes'" class="result-card notes-card">
          <h2>My Notes</h2>
          
          <!-- Add new note form -->
          <div class="add-note-form">
            <h3>Add New Note</h3>
            <div class="form-group">
              <label for="note-title">Title</label>
              <input
                id="note-title"
                v-model="newNoteTitle"
                type="text"
                placeholder="Enter note title"
                class="note-input"
              />
            </div>
            <div class="form-group">
              <label for="note-content">Content</label>
              <textarea
                id="note-content"
                v-model="newNoteContent"
                placeholder="Enter note content"
                rows="5"
                class="note-textarea"
              ></textarea>
            </div>
            <button @click="createNote" :disabled="!newNoteTitle || !newNoteContent || notesLoading" class="add-note-button">
              {{ notesLoading ? 'Creating...' : 'Create Note' }}
            </button>
            <div v-if="noteError" class="error-message">{{ noteError }}</div>
            <div v-if="noteSuccess" class="success-message">{{ noteSuccess }}</div>
          </div>
          
          <!-- Notes list -->
          <div class="notes-list">
            <h3>Your Notes ({{ notes.length }})</h3>
            <div v-if="notesLoading && notes.length === 0" class="loading">Loading notes...</div>
            <div v-else-if="notes.length === 0" class="no-notes">No notes yet. Create your first note above!</div>
            <div v-else class="notes-items">
              <div v-for="note in notes" :key="note.id" class="note-item">
                <div class="note-header">
                  <h4>{{ note.title }}</h4>
                  <button @click="deleteNote(note.id)" class="delete-button" :disabled="notesLoading">Delete</button>
                </div>
                <div class="note-meta">
                  <span>Created: {{ formatDate(note.created_at) }}</span>
                  <button @click="downloadNote(note.id, note.title)" class="download-button" :disabled="notesLoading">Download TXT</button>
                </div>
              </div>
            </div>
          </div>
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
import { auth } from '../utils/auth'

export default {
  name: 'Welcome',
  data() {
    return {
      currentView: null,
      luckyNumber: null,
      quote: null,
      loading: false,
      notes: [],
      notesLoading: false,
      newNoteTitle: '',
      newNoteContent: '',
      noteError: '',
      noteSuccess: ''
    }
  },
  async mounted() {
    // Verify authentication on mount
    if (!auth.isAuthenticated()) {
      this.$router.push('/')
      return
    }
    
    try {
      await axios.get('/api/welcome/')
    } catch (err) {
      // If not authenticated, redirect to login
      if (err.response?.status === 401) {
        auth.clearTokens()
        this.$router.push('/')
      }
    }
  },
  methods: {
    async showLuckyNumber() {
      this.currentView = 'lucky'
      this.luckyNumber = null
      this.loading = true
      
      try {
        const response = await axios.get('/api/lucky-number/')
        this.luckyNumber = response.data.number
      } catch (err) {
        console.error('Error fetching lucky number:', err)
        this.luckyNumber = 'Error loading number'
        if (err.response?.status === 401) {
          auth.clearTokens()
          this.$router.push('/')
        }
      } finally {
        this.loading = false
      }
    },
    async showQuote() {
      this.currentView = 'quote'
      this.quote = null
      this.loading = true
      
      try {
        const response = await axios.get('/api/quote-of-the-day/')
        this.quote = response.data.quote
      } catch (err) {
        console.error('Error fetching quote:', err)
        this.quote = 'Error loading quote'
        if (err.response?.status === 401) {
          auth.clearTokens()
          this.$router.push('/')
        }
      } finally {
        this.loading = false
      }
    },
    async showNotes() {
      this.currentView = 'notes'
      this.notesLoading = true
      this.noteError = ''
      this.noteSuccess = ''
      
      try {
        const response = await axios.get('/api/notes/')
        this.notes = response.data.notes || []
      } catch (err) {
        console.error('Error fetching notes:', err)
        this.noteError = 'Failed to load notes'
        if (err.response?.status === 401) {
          auth.clearTokens()
          this.$router.push('/')
        }
      } finally {
        this.notesLoading = false
      }
    },
    async createNote() {
      if (!this.newNoteTitle.trim() || !this.newNoteContent.trim()) {
        this.noteError = 'Title and content are required'
        return
      }
      
      this.notesLoading = true
      this.noteError = ''
      this.noteSuccess = ''
      
      try {
        const response = await axios.post('/api/notes/create/', {
          title: this.newNoteTitle,
          content: this.newNoteContent
        })
        
        this.noteSuccess = 'Note created successfully!'
        this.newNoteTitle = ''
        this.newNoteContent = ''
        
        // Reload notes list
        await this.showNotes()
      } catch (err) {
        this.noteError = err.response?.data?.error || 'Failed to create note'
        if (err.response?.status === 401) {
          auth.clearTokens()
          this.$router.push('/')
        }
      } finally {
        this.notesLoading = false
      }
    },
    async deleteNote(noteId) {
      if (!confirm('Are you sure you want to delete this note?')) {
        return
      }
      
      this.notesLoading = true
      this.noteError = ''
      this.noteSuccess = ''
      
      try {
        await axios.delete(`/api/notes/${noteId}/delete/`)
        
        this.noteSuccess = 'Note deleted successfully!'
        
        // Reload notes list
        await this.showNotes()
      } catch (err) {
        this.noteError = err.response?.data?.error || 'Failed to delete note'
        if (err.response?.status === 401) {
          auth.clearTokens()
          this.$router.push('/')
        }
      } finally {
        this.notesLoading = false
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    async downloadNote(noteId, noteTitle) {
      try {
        const response = await axios.get(`/api/notes/${noteId}/download/`, {
          responseType: 'blob'
        })
        
        // Create a blob URL and trigger download
        const blob = new Blob([response.data], { type: 'text/plain' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${noteTitle}.txt`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Error downloading note:', err)
        this.noteError = err.response?.data?.error || 'Failed to download note'
        if (err.response?.status === 401) {
          auth.clearTokens()
          this.$router.push('/')
        }
      }
    },
    async handleLogout() {
      try {
        await axios.post('/api/logout/')
      } catch (err) {
        console.error('Logout error:', err)
      } finally {
        // Clear tokens and redirect to login
        auth.clearTokens()
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

/* Notes styles */
.notes-card {
  text-align: left;
  max-width: 900px;
}

.add-note-form {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #e0e0e0;
}

.add-note-form h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

.note-input,
.note-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s;
}

.note-input:focus,
.note-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.note-textarea {
  resize: vertical;
  min-height: 120px;
}

.add-note-button {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.add-note-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.add-note-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 1rem;
  text-align: center;
}

.success-message {
  background: #efe;
  color: #3c3;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 1rem;
  text-align: center;
}

.notes-list h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.no-notes {
  text-align: center;
  color: #999;
  padding: 2rem;
  font-style: italic;
}

.notes-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.note-item {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: box-shadow 0.2s;
}

.note-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.note-header h4 {
  color: #333;
  margin: 0;
  font-size: 1.2rem;
  flex: 1;
}

.delete-button {
  padding: 0.5rem 1rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.delete-button:hover:not(:disabled) {
  background: #c82333;
}

.delete-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #666;
  font-size: 0.9rem;
}

.download-button {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  text-decoration: none;
}

.download-button:hover:not(:disabled) {
  background: #764ba2;
}

.download-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  
  .note-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .note-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
