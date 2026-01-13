# MFA App

Simple login application with Vue.js frontend and Django REST Framework backend.

## Setup Instructions

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

1. Open `http://localhost:5173` in your browser
2. Login with:
   - Username: `admin`
   - Password: `admin`
3. You will be redirected to the welcome page showing "Success!"

## Project Structure

```
mfa/
├── backend/
│   ├── api/          # API endpoints
│   ├── config/       # Django settings
│   └── manage.py
├── frontend/
│   └── src/
│       ├── views/    # Login and Welcome pages
│       ├── router/   # Vue Router configuration
│       └── App.vue
└── README.md
```
