# Apex Telemetry — Formula 1 Data Visualization Platform

A Flask-based web application for analyzing and comparing Formula 1 telemetry data using the OpenF1 API. Features interactive charts with zoom/pan capabilities, driver comparison tools, and sector-by-sector performance analysis.

## Features

### 🔐 User Authentication
- Secure registration and login with bcrypt password hashing
- Flask-Login for session management
- User-specific data isolation

### 📊 F1 Data Viewer
- Browse historical F1 races from multiple seasons
- Filter by year, country, meeting, and session type
- View real-time telemetry for any driver:
  - Speed traces
  - RPM progression
  - Throttle and brake inputs
  - Lap times
  - Position changes

### 🏁 Driver Comparison
- Side-by-side telemetry comparison between two drivers
- Compare:
  - Speed profiles
  - Engine RPM patterns
  - Throttle/brake techniques
  - Sector-by-sector performance
  - Lap time consistency
- Side-by-side sector time analysis
- Interactive charts with zoom and pan

### 📈 Sector Breakdown
- Detailed sector-by-sector performance analysis
- Track sector time progression across laps
- Sector time distribution visualization
- Individual sector performance charts
- Statistics showing fastest times per sector
- Export capabilities

### 📥 Data Export
- Export telemetry data as **CSV** or **JSON**
- Available for:
  - Car telemetry (speed, RPM, throttle, brake, gear)
  - Lap data (lap times, sector times, intermediate speeds)
  - Position data

### 📊 Interactive Charts
- Built with Chart.js and chartjs-plugin-zoom
- Zoom with mouse wheel or pinch gesture
- Pan mode for exploring large datasets
- Full-screen expandable chart modals
- Reset zoom button for returning to original view

### 💾 Session Management
- Save and organize F1 telemetry sessions
- Edit and delete saved sessions
- Persistent storage with SQLite

### 🎨 F1-Themed UI
- Ferrari red accent color (#DC0000)
- Dark theme matching modern F1 broadcast aesthetics
- Responsive Bootstrap 5 layout
- Smooth animations and hover effects

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation (Windows PowerShell)

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Open http://127.0.0.1:5000 in your browser

### Default Credentials (local development)
- Register a new account with any email/password

## Usage

### Viewing F1 Data
1. Go to **F1 Viewer**
2. Select Year → Country → Meeting → Session
3. Choose a driver
4. Browse real-time telemetry charts
5. Click 🔍 to expand any chart for detailed analysis

### Comparing Drivers
1. Go to **Comparison**
2. Select Year → Country → Meeting → Session
3. Choose Driver 1 and Driver 2
4. Click **COMPARE DRIVERS**
5. Analyze side-by-side telemetry across 7 different metrics
6. Export data for external analysis

### Analyzing Sectors
1. Go to **Sectors**
2. Select Year → Country → Meeting → Session → Driver
3. Click **LOAD SECTOR DATA**
4. View sector progression across all laps
5. Compare sector time distribution
6. Check statistics for fastest times
7. Export lap data with all sector information

### Exporting Data
- Each telemetry view includes export buttons
- Choose between **CSV** (Excel-compatible) or **JSON** (raw data)
- Exported files include all available fields from OpenF1 API

## Project Structure

```
├── app.py                      # Flask application & routes
├── f1_api.py                   # OpenF1 API service layer
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── static/
│   └── css/
│       └── style.css           # F1-themed styling
└── templates/
    ├── base.html               # Master template with navbar & modals
    ├── dashboard.html          # Main dashboard
    ├── f1_viewer.html          # F1 telemetry viewer
    ├── driver_comparison.html   # Driver comparison tool
    ├── sector_breakdown.html    # Sector analysis tool
    ├── register.html           # User registration
    ├── login.html              # User login
    ├── sessions.html           # Saved sessions list
    ├── session_form.html       # Session create/edit
    └── index.html              # Landing page
```

## Technology Stack

- **Backend**: Flask 2.0+, SQLAlchemy ORM
- **Database**: SQLite
- **Authentication**: Flask-Bcrypt, Flask-Login
- **Frontend**: Bootstrap 5.3.0, Chart.js
- **Charting**: Chart.js with chartjs-plugin-zoom 2.1.0
- **API**: OpenF1 (free, no authentication required)
- **Hosting**: Configured for Render with gunicorn

## API Routes

### Public Routes
- `GET /` - Landing page
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Protected Routes (login required)
- `GET /dashboard` - Main dashboard
- `GET /f1-viewer` - F1 telemetry viewer
- `GET /driver-comparison` - Driver comparison tool
- `GET /sector-breakdown` - Sector analysis tool
- `GET /sessions` - List user's saved sessions
- `POST /sessions/new` - Create new session
- `POST /sessions/<id>/edit` - Edit session
- `POST /sessions/<id>/delete` - Delete session

### API Endpoints (login required)
- `GET /api/f1/meetings` - Get F1 races (params: year, country)
- `GET /api/f1/sessions` - Get sessions (params: meeting_key)
- `GET /api/f1/drivers` - Get drivers (params: session_key)
- `GET /api/f1/car-data` - Get telemetry (params: session_key, driver_number)
- `GET /api/f1/lap-data` - Get lap times (params: session_key, driver_number)
- `GET /api/f1/sector-data` - Get sector data (params: session_key, driver_number)
- `GET /api/f1/position-data` - Get position changes (params: session_key, driver_number)
- `GET /api/f1/compare-drivers` - Compare two drivers (params: session_key, driver_1, driver_2)
- `GET /api/export/telemetry` - Export car data (params: session_key, driver_number, format: csv|json)
- `GET /api/export/lap-data` - Export lap data (params: session_key, driver_number, format: csv|json)

## Deployment

### Deploy to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set environment variables:
   - `SECRET_KEY` - Random secret key for sessions
   - `DATABASE_URL` - SQLite path (optional, defaults to local)
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app`

### Environment Variables

```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///apex_telemetry.db
FLASK_ENV=production
```

## Data Source

All F1 data comes from the **OpenF1 API**:
- Free, no authentication required
- Historical data for recent F1 seasons
- Real-time and recorded telemetry
- Comprehensive driver and session information

## Future Enhancements

- [ ] Email notifications for race events
- [ ] Multi-driver comparison (3+ drivers)
- [ ] Advanced filtering and search
- [ ] Performance anomaly detection
- [ ] Predictive analytics
- [ ] Real-time race data (with live updates)
- [ ] Custom telemetry overlays
- [ ] Team-wide performance analysis

## Troubleshooting

### Charts not loading
- Check browser console for JavaScript errors
- Verify Chart.js CDN is accessible
- Clear browser cache

### API data not appearing
- Ensure you have internet connection (OpenF1 API requires it)
- Verify session_key is valid for the selected meeting
- Check if driver participated in that session

### Database errors
- Delete `apex_telemetry.db` and restart app to reset
- Ensure database file path is writable

## License

Confidential - Apex Telemetry Project

## Support

For issues or feature requests, contact development team.
