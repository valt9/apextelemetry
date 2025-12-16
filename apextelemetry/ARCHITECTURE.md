# Apex Telemetry - Architecture & Workflow

## Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Bootstrap  │  │   Chart.js   │  │ Flask Templates│    │
│  │      UI      │  │  Visualizations│ │   (Jinja2)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      Flask Application                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │ Authentication│  │   CRUD Ops    │     │
│  │  (app.py)    │  │ (Flask-Login) │  │  (Sessions)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   SQLite     │  │  F1 API      │  │ Email Service │     │
│  │  Database    │  │  Service     │  │ (Flask-Mail)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## User Workflow

### 1. Authentication Flow

```
User → Register/Login → Flask-Bcrypt (password hashing) → SQLite (user storage)
```

### 1a. Account Management Flow
```
User → Dashboard → Change Password (current password required, strong new password) → Bcrypt update in SQLite
User → Dashboard → Delete Account → Cascade delete user and all related data
```

### 2. Session Creation Flow
```
User → New Session Form → Flask Route → F1 API Service → Data Processing → SQLite Storage → Email Notification → Dashboard
```

### 3. Data Visualization Flow
```
User → Select Session → Flask Route → SQLite Query → JSON API → Chart.js → Interactive Dashboard
```

### 4. CRUD Operations

**Create:**
- User creates new race session
- System fetches data from F1 API
- Data stored in database
- Email notification sent

**Read:**
- User views dashboard (all sessions)
- User views session details (charts and metrics)

**Update:**
- User refreshes session data
- System detects pit stops
- Email notification sent

**Delete:**
- User deletes session
- Associated data cascade deleted

## Database Schema

```
User
├── id (PK)
├── username (unique)
├── email (unique)
├── password (hashed)
└── created_at

RaceSession
├── id (PK)
├── name
├── driver_name
├── race_date
├── created_at
└── user_id (FK → User.id)

CarData
├── id (PK)
├── session_id (FK → RaceSession.id)
├── speed
├── rpm
├── lap_time
├── tire_temp
├── tire_wear
├── sector_time
├── position
└── timestamp
```

## Key Features Implementation

### 1. Authentication
- **Flask-Login**: Manages user sessions
- **Flask-Bcrypt**: Hashes passwords securely
- **Session Management**: Tracks logged-in users

### 2. F1 Data Integration
- **Ergast F1 API**: Fetches driver information
- **Simulated Telemetry**: Generates realistic race data
- **Data Processing**: Converts API data to database format

### 3. Visualizations
- **Chart.js**: Multiple chart types (line, bar)
- **Real-time Updates**: AJAX data fetching
- **Interactive Dashboards**: Multiple metrics displayed

### 4. Email Notifications
- **Flask-Mail**: SMTP email sending
- **Event Detection**: Pit stops, session creation
- **User Alerts**: Race completion notifications

## Security Features

1. **Password Hashing**: Bcrypt with salt
2. **Session Protection**: Login required for protected routes
3. **User Isolation**: Users can only access their own data
4. **SQL Injection Protection**: SQLAlchemy ORM
5. **Change Password**: Requires current password, strong new password, and prevents reuse of current password
6. **Account Deletion**: User can permanently delete their account and all data

## Deployment Architecture (Render)

```
Git Repository → Render Platform → Build (pip install) → Run (gunicorn) → Web Service
```

## Data Flow Example

1. User logs in → Session created
2. User creates "Monaco GP 2024" session for "Lewis Hamilton"
3. System calls F1 API → Gets driver info
4. System generates 50 laps of telemetry data
5. Data stored in SQLite (CarData table)
6. Email sent to user
7. User views dashboard → Charts render with Chart.js
8. User refreshes data → Pit stops detected → Email sent

