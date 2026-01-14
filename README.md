# MFA App

Simple login application with Vue.js frontend and Django REST Framework backend, featuring Multi-Factor Authentication (MFA) using Google Authenticator.

## Quick Start with Docker Compose (Recommended)

1. Make sure Docker and Docker Compose are installed on your system.

2. Build and start all services:
```bash
docker-compose up --build
```

3. The application will be available at:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`

4. Login credentials:
   - Username: `admin`
   - Password: `admin`

5. Access Django Admin Panel:
   - URL: `http://localhost:8000/admin/`
   - Use the same credentials (admin/admin)
   - You can create and manage users (including non-admin users) from the admin panel

6. To stop the services:
```bash
docker-compose down
```

7. To view logs:
```bash
docker-compose logs -f
```

8. To reset MFA (if needed):
```bash
docker-compose exec backend python reset_mfa.py
```

9. To create database migrations (after adding Note model):
```bash
docker-compose exec backend python manage.py makemigrations api
docker-compose exec backend python manage.py migrate
```

## Django Admin Panel

The Django admin panel is available at `http://localhost:8000/admin/` (or `http://backend:8000/admin/` from within Docker).

### Access
- URL: `http://localhost:8000/admin/`
- Username: `admin`
- Password: `admin`

### Features
- **User Management**: Create, edit, and delete users
  - To create a **non-admin user**: 
    1. Go to "Users" → "Add user"
    2. Enter username and password
    3. **Uncheck** "Staff status" and "Superuser status" checkboxes
    4. Click "Save"
- **MFA Device Management**: View and manage TOTP devices for users
- **Session Management**: View active sessions

## Django Admin Panel

The Django admin panel is available at `http://localhost:8000/admin/` (or `http://backend:8000/admin/` from within Docker).

### Access
- URL: `http://localhost:8000/admin/`
- Username: `admin`
- Password: `admin`

### Features
- **User Management**: Create, edit, and delete users
  - To create a **non-admin user**: 
    1. Go to "Users" → "Add user"
    2. Enter username and password
    3. **Uncheck** "Staff status" and "Superuser status" checkboxes
    4. Click "Save"
- **MFA Device Management**: View and manage TOTP devices for users
- **Session Management**: View active sessions

## Manual Setup Instructions (Without Docker)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (username: admin, password: admin):
```bash
python manage.py migrate
python create_admin.py
```

Alternatively, you can use the Django createsuperuser command:
```bash
python manage.py createsuperuser
```
When prompted, use:
- Username: `admin`
- Password: `admin`
- Email: (press Enter to skip)

6. Run the Django server:
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### First Time Login (Without MFA)

1. Open `http://localhost:5173` in your browser
2. Login with:
   - Username: `admin`
   - Password: `admin`
3. You will be redirected to the welcome page showing "Hello" message
4. Use the navigation bar to:
   - Click "Lucky Number" to generate a random number (1-100)
   - Click "Quote of the day" to see a random inspirational quote

### Setting Up MFA

1. After logging in, click "Setup MFA" on the welcome page
2. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
3. Enter the 6-digit code from your app to confirm setup
4. MFA is now enabled for your account

### Logging In With MFA

1. Enter your username and password
2. If MFA is enabled, you'll be redirected to the MFA verification page
3. Enter the 6-digit code from your authenticator app
4. You'll be redirected to the welcome page upon successful verification

### Resetting MFA

If you need to reset MFA for the admin user (development purposes):

1. Navigate to the backend directory:
```bash
cd backend
```

2. Run the reset script:
```bash
python reset_mfa.py
```

This will delete all MFA devices for the admin user. On the next login, you'll be required to set up MFA again.

**Note:** Make sure the Django server is stopped or the database is not locked when running this script.

## API Endpoints

- `POST /api/login/` - Login with username and password
- `POST /api/logout/` - Logout user
- `POST /api/mfa/verify/` - Verify MFA token during login
- `GET /api/mfa/setup/` - Get QR code for MFA setup
- `POST /api/mfa/confirm/` - Confirm MFA setup with verification code
- `GET /api/welcome/` - Welcome page (requires authentication)
- `GET /api/lucky-number/` - Generate a random lucky number (1-100)
- `GET /api/quote-of-the-day/` - Get a random inspirational quote
- `GET /api/notes/` - Get all notes for authenticated user
- `POST /api/notes/create/` - Create a new note (requires title and content)
- `DELETE /api/notes/<id>/delete/` - Delete a note

## Project Structure

```
mfa/
├── backend/
│   ├── api/          # API endpoints (login, MFA)
│   ├── config/       # Django settings
│   ├── Dockerfile    # Backend Docker configuration
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── views/    # Login, Welcome, MFA Setup, MFA Verify
│   │   ├── router/   # Vue Router configuration
│   │   └── App.vue
│   └── Dockerfile    # Frontend Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── README.md
```

## MFA Features

- TOTP (Time-based One-Time Password) support
- QR code generation for easy setup
- Compatible with Google Authenticator, Authy, and other TOTP apps
- Optional MFA - users can choose to enable it
- Secure session-based authentication flow
