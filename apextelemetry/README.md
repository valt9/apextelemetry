# Apex Telemetry - F1 Data Dashboard

A web application for visualizing Formula 1 telemetry data with interactive dashboards, CRUD operations, and real-time data analysis.

## Features

- User authentication and session management
- Change password and delete account features
- Interactive dashboards with Chart.js visualizations
- F1 API integration for historical and live data
- CRUD operations for cars and race sessions
- Email notifications for race events
- Responsive Bootstrap UI

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
SECRET_KEY=your-secret-key-here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

3. Run the application:
```bash
python app.py
```

4. Access the application at `http://localhost:5000`

## Technology Stack

- **Frontend**: Chart.js, Flask Templates, Bootstrap
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Authentication**: Flask-Bcrypt
- **Hosting**: Render (ready for deployment)

## Account Management

- **Change Password**: Users can securely update their password from the dashboard. Passwords must meet strength requirements (8+ chars, uppercase, lowercase, number) and cannot be reused.
- **Delete Account**: Users can permanently delete their account and all associated data from the dashboard.

## Security Features

- Passwords are hashed with bcrypt and never stored in plain text
- Password change requires current password verification and strong new password
- Session management with Flask-Login and Flask-Session
- User isolation: users can only access their own data
- SQL injection protection via SQLAlchemy ORM

## Usage

1. Register or log in to your account
2. Create and manage race sessions, compare drivers, and view telemetry data
3. Use the dashboard's Account Actions to change your password or delete your account

## Screenshots

_Add screenshots of the dashboard, change password, and account deletion pages here_

## References

### Major Libraries

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Flask-Bcrypt](https://flask-bcrypt.readthedocs.io/) - Password hashing
- [Flask-Login](https://flask-login.readthedocs.io/) - User session management
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) - ORM/database
- [Flask-Session](https://flask-session.readthedocs.io/) - Server-side session storage
- [Flask-Mail](https://pythonhosted.org/Flask-Mail/) - Email notifications
- [requests](https://docs.python-requests.org/) - HTTP requests
- [Chart.js](https://www.chartjs.org/) - Data visualization (frontend)
- [Bootstrap](https://getbootstrap.com/) - Responsive UI (frontend)

### APIs

- [Ergast Developer API](https://ergast.com/mrd/) - Formula 1 data (drivers, races, results)

