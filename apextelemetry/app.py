from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session as flask_session, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, RaceSession, CarData, Comparison
from f1_api import F1APIService
from datetime import datetime, timedelta
import os
import json
import ast
from dotenv import load_dotenv

# Optional email support
try:
    from flask_mail import Mail, Message
    MAIL_AVAILABLE = True
except ImportError:
    MAIL_AVAILABLE = False
    print("Warning: Flask-Mail not installed. Email notifications will be disabled.")

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apextelemetry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)

if MAIL_AVAILABLE:
    mail = Mail(app)
else:
    mail = None

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize Flask-Session
try:
    from flask_session import Session
    Session(app)
except ImportError:
    print("Warning: Flask-Session not installed. Using cookie-based sessions (limited to 4KB).")

f1_api = F1APIService()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    sessions = RaceSession.query.filter_by(user_id=current_user.id).all()
    comparisons = Comparison.query.filter_by(user_id=current_user.id).order_by(Comparison.created_at.desc()).all()
    return render_template('dashboard.html', sessions=sessions, comparisons=comparisons)

@app.route('/session/new', methods=['GET', 'POST'])
@login_required
def new_session():
    if request.method == 'POST':
        session_name = request.form.get('session_name')
        driver_name = request.form.get('driver_name')
        race_selection = request.form.get('race_selection')  # Format: "year|round|date"
        
        # Parse race selection
        if race_selection:
            parts = race_selection.split('|')
            race_year = int(parts[0]) if len(parts) > 0 else datetime.now().year
            race_round = int(parts[1]) if len(parts) > 1 else 1
            race_date = parts[2] if len(parts) > 2 else datetime.now().strftime('%Y-%m-%d')
        else:
            race_date = datetime.now().strftime('%Y-%m-%d')
            race_year = datetime.now().year
            race_round = 1
        
        # Create new session
        race_session = RaceSession(
            name=session_name,
            driver_name=driver_name,
            race_date=datetime.strptime(race_date, '%Y-%m-%d') if race_date else datetime.now(),
            user_id=current_user.id
        )
        db.session.add(race_session)
        db.session.commit()
        
        # Fetch data from F1 API
        try:
            data = f1_api.fetch_race_data(driver_name, race_date)
            if data:
                for entry in data:
                    car_data = CarData(
                        session_id=race_session.id,
                        speed=entry.get('speed', 0),
                        rpm=entry.get('rpm', 0),
                        lap_time=entry.get('lap_time', 0),
                        tire_temp=entry.get('tire_temp', 0),
                        tire_wear=entry.get('tire_wear', 0),
                        sector_time=entry.get('sector_time', 0),
                        position=entry.get('position', 0),
                        timestamp=entry.get('timestamp', datetime.now())
                    )
                    db.session.add(car_data)
                db.session.commit()
                
                # Send notification email
                session_url = url_for('view_session', session_id=race_session.id, _external=True)
                send_notification_email(
                    current_user,
                    f"New F1 Session Created: {session_name}",
                    f"Your F1 telemetry session '{session_name}' for driver {driver_name} has been created successfully.\n\n"
                    f"Race Date: {race_date}\n"
                    f"Data Points: {len(data)}\n\n"
                    f"View your session at: {session_url}"
                )
                
                flash('Session created and historical data fetched successfully!', 'success')
            else:
                flash('No data found for the specified driver/date', 'warning')
        except Exception as e:
            flash(f'Error fetching data: {str(e)}', 'error')
        
        return redirect(url_for('view_session', session_id=race_session.id))
    
    # GET request - show form with all historical drivers
    drivers = f1_api.get_drivers()
    return render_template('new_session.html', drivers=drivers)

@app.route('/session/<int:session_id>')
@login_required
def view_session(session_id):
    race_session = RaceSession.query.get_or_404(session_id)
    
    if race_session.user_id != current_user.id:
        flash('You do not have access to this session', 'error')
        return redirect(url_for('dashboard'))
    
    car_data = CarData.query.filter_by(session_id=session_id).order_by(CarData.timestamp).all()
    return render_template('view_session.html', session=race_session, car_data=car_data)

@app.route('/session/<int:session_id>/data')
@login_required
def get_session_data(session_id):
    race_session = RaceSession.query.get_or_404(session_id)
    
    if race_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    car_data = CarData.query.filter_by(session_id=session_id).order_by(CarData.timestamp).all()
    
    data = {
        'timestamps': [d.timestamp.isoformat() for d in car_data],
        'speed': [d.speed for d in car_data],
        'rpm': [d.rpm for d in car_data],
        'lap_time': [d.lap_time for d in car_data],
        'tire_temp': [d.tire_temp for d in car_data],
        'tire_wear': [d.tire_wear for d in car_data],
        'sector_time': [d.sector_time for d in car_data],
        'position': [d.position for d in car_data]
    }
    
    return jsonify(data)

@app.route('/session/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_session(session_id):
    race_session = RaceSession.query.get_or_404(session_id)
    
    if race_session.user_id != current_user.id:
        flash('You do not have access to this session', 'error')
        return redirect(url_for('dashboard'))
    
    # Delete associated car data
    CarData.query.filter_by(session_id=session_id).delete()
    db.session.delete(race_session)
    db.session.commit()
    
    flash('Session deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/session/<int:session_id>/update', methods=['POST'])
@login_required
def update_session(session_id):
    race_session = RaceSession.query.get_or_404(session_id)
    
    if race_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    if 'name' in data:
        race_session.name = data['name']
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/drivers')
@login_required
def get_drivers():
    drivers = f1_api.get_drivers()
    return jsonify(drivers)

@app.route('/api/driver-races/<driver_name>')
@login_required
def get_driver_races(driver_name):
    """Get all races for a specific driver"""
    races = f1_api.get_races_for_driver(driver_name)
    return jsonify(races)

@app.route('/api/years')
@login_required
def get_available_years():
    """Get list of all available years with historical race data"""
    years = f1_api.get_available_years()
    return jsonify(years)

@app.route('/api/refresh-data/<int:session_id>', methods=['POST'])
@login_required
def refresh_data(session_id):
    race_session = RaceSession.query.get_or_404(session_id)
    
    if race_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = f1_api.fetch_race_data(race_session.driver_name, race_session.race_date.strftime('%Y-%m-%d'))
        if data:
            # Clear existing data
            CarData.query.filter_by(session_id=session_id).delete()
            
            # Check for pit stops (significant tire wear changes)
            previous_wear = None
            pit_stops = []
            
            for entry in data:
                car_data = CarData(
                    session_id=race_session.id,
                    speed=entry.get('speed', 0),
                    rpm=entry.get('rpm', 0),
                    lap_time=entry.get('lap_time', 0),
                    tire_temp=entry.get('tire_temp', 0),
                    tire_wear=entry.get('tire_wear', 0),
                    sector_time=entry.get('sector_time', 0),
                    position=entry.get('position', 0),
                    timestamp=entry.get('timestamp', datetime.now())
                )
                db.session.add(car_data)
                
                # Detect pit stops (tire wear drops significantly)
                if previous_wear is not None and entry.get('tire_wear', 0) < previous_wear - 20:
                    pit_stops.append(entry.get('lap', 0))
                previous_wear = entry.get('tire_wear', 0)
            
            db.session.commit()
            
            # Send notification if pit stops detected
            if pit_stops:
                session_url = url_for('view_session', session_id=race_session.id, _external=True)
                send_notification_email(
                    current_user,
                    f"Pit Stop Detected: {race_session.name}",
                    f"Pit stops detected in session '{race_session.name}' at laps: {', '.join(map(str, pit_stops))}\n\n"
                    f"View updated data at: {session_url}"
                )
            
            return jsonify({'success': True, 'message': 'Data refreshed successfully', 'pit_stops': pit_stops})
        else:
            return jsonify({'success': False, 'message': 'No data found'})
    except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/compare', methods=['GET', 'POST'])
@login_required
def compare_drivers():
    """Compare two drivers' historical data"""
    if request.method == 'POST':
        driver1_name = request.form.get('driver1_name')
        driver2_name = request.form.get('driver2_name')
        race_selection = request.form.get('race_selection')  # Format: "year|round|date"
        
        if not driver1_name or not driver2_name or not race_selection:
            flash('Please select both drivers and a race', 'error')
            return redirect(url_for('compare_drivers'))
        
        if driver1_name == driver2_name:
            flash('Please select two different drivers', 'error')
            return redirect(url_for('compare_drivers'))
        
        # Parse race selection
        parts = race_selection.split('|')
        race_date = parts[2] if len(parts) > 2 else datetime.now().strftime('%Y-%m-%d')
        
        # Fetch data for both drivers
        try:
            data1 = f1_api.fetch_race_data(driver1_name, race_date)
            data2 = f1_api.fetch_race_data(driver2_name, race_date)
            
            if not data1 or not data2:
                flash('Could not fetch data for one or both drivers', 'error')
                return redirect(url_for('compare_drivers'))
            
            # Convert datetime objects to strings for JSON serialization
            def serialize_data(data):
                result = []
                for entry in data:
                    serialized = {}
                    for key, value in entry.items():
                        if isinstance(value, datetime):
                            serialized[key] = value.isoformat()
                        else:
                            serialized[key] = value
                    result.append(serialized)
                return result
            
            data1_serialized = serialize_data(data1)
            data2_serialized = serialize_data(data2)
            
            # Store data in session to avoid form size limits
            flask_session['comparison_data1'] = data1_serialized
            flask_session['comparison_data2'] = data2_serialized
            flask_session['comparison_driver1'] = driver1_name
            flask_session['comparison_driver2'] = driver2_name
            flask_session['comparison_race_date'] = race_date
            
            return render_template('compare_results.html', 
                                 driver1_name=driver1_name,
                                 driver2_name=driver2_name,
                                 race_date=race_date,
                                 data1=data1_serialized,
                                 data2=data2_serialized)
        except Exception as e:
            flash(f'Error fetching comparison data: {str(e)}', 'error')
            return redirect(url_for('compare_drivers'))
    
    # GET request - show selection form
    drivers = f1_api.get_drivers()
    return render_template('compare.html', drivers=drivers)

@app.route('/api/compare-data', methods=['POST'])
@login_required
def get_compare_data():
    """API endpoint to get comparison data for two drivers"""
    data = request.json
    driver1_name = data.get('driver1_name')
    driver2_name = data.get('driver2_name')
    race_date = data.get('race_date')
    
    if not driver1_name or not driver2_name or not race_date:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        data1 = f1_api.fetch_race_data(driver1_name, race_date)
        data2 = f1_api.fetch_race_data(driver2_name, race_date)
        
        if not data1 or not data2:
            return jsonify({'error': 'Could not fetch data for one or both drivers'}), 404
        
        # Format data for comparison
        result = {
            'driver1': {
                'name': driver1_name,
                'speed': [d.get('speed', 0) for d in data1],
                'rpm': [d.get('rpm', 0) for d in data1],
                'lap_time': [d.get('lap_time', 0) for d in data1],
                'tire_temp': [d.get('tire_temp', 0) for d in data1],
                'tire_wear': [d.get('tire_wear', 0) for d in data1],
                'sector_time': [d.get('sector_time', 0) for d in data1],
                'position': [d.get('position', 0) for d in data1],
                'timestamps': [d.get('timestamp', datetime.now()).isoformat() if isinstance(d.get('timestamp'), datetime) else str(d.get('timestamp', '')) for d in data1]
            },
            'driver2': {
                'name': driver2_name,
                'speed': [d.get('speed', 0) for d in data2],
                'rpm': [d.get('rpm', 0) for d in data2],
                'lap_time': [d.get('lap_time', 0) for d in data2],
                'tire_temp': [d.get('tire_temp', 0) for d in data2],
                'tire_wear': [d.get('tire_wear', 0) for d in data2],
                'sector_time': [d.get('sector_time', 0) for d in data2],
                'position': [d.get('position', 0) for d in data2],
                'timestamps': [d.get('timestamp', datetime.now()).isoformat() if isinstance(d.get('timestamp'), datetime) else str(d.get('timestamp', '')) for d in data2]
            }
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/comparison/save', methods=['POST'])
@login_required
def save_comparison():
    # Get data from session instead of form to avoid size limits
    data1_parsed = flask_session.pop('comparison_data1', None)
    data2_parsed = flask_session.pop('comparison_data2', None)
    driver1_name = flask_session.pop('comparison_driver1', None)
    driver2_name = flask_session.pop('comparison_driver2', None)
    race_date = flask_session.pop('comparison_race_date', None)

    if not all([driver1_name, driver2_name, data1_parsed, data2_parsed]):
        flash('Comparison data not found. Please generate a comparison first.', 'error')
        return redirect(url_for('dashboard'))

    comparison = Comparison(
        user_id=current_user.id,
        driver1_name=driver1_name,
        driver2_name=driver2_name,
        data1=json.dumps(data1_parsed),  # Store as clean JSON
        data2=json.dumps(data2_parsed),
        race_date=race_date
    )
    db.session.add(comparison)
    db.session.commit()
    flash('Comparison saved successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/comparison/<int:comp_id>/delete', methods=['POST'])
@login_required
def delete_comparison(comp_id):
    comparison = Comparison.query.get_or_404(comp_id)
    
    if comparison.user_id != current_user.id:
        flash('You do not have access to this comparison', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(comparison)
    db.session.commit()
    
    flash('Comparison deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/comparison/<int:comp_id>')
@login_required
def view_comparison(comp_id):
    comp = Comparison.query.get_or_404(comp_id)
    if comp.user_id != current_user.id:
        abort(403)

    def clean_json(s):
        # Replace JSON representations of NaN and Infinity with null
        s = s.replace('"NaN"', 'null').replace('"Infinity"', 'null').replace('"-Infinity"', 'null')
        return s

    data1_str = clean_json(comp.data1)
    data2_str = clean_json(comp.data2)

    def parse_data(s):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(s)
            except (ValueError, SyntaxError):
                raise ValueError("Invalid data format")

    try:
        data1 = parse_data(data1_str)
        data2 = parse_data(data2_str)
    except ValueError as e:
        flash(f'Error loading comparison data: {e}', 'error')
        return redirect(url_for('dashboard'))

    return render_template('compare_results.html', 
                         driver1_name=comp.driver1_name, 
                         driver2_name=comp.driver2_name, 
                         data1=data1, 
                         data2=data2, 
                         race_date=comp.race_date)

@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    # Count user's data for confirmation display
    session_count = RaceSession.query.filter_by(user_id=current_user.id).count()
    comparison_count = Comparison.query.filter_by(user_id=current_user.id).count()
    
    if request.method == 'POST':
        # Check confirmation
        confirmation = request.form.get('confirmation', '').strip()
        if confirmation != 'DELETE':
            flash('Please type "DELETE" to confirm account deletion.', 'error')
            return redirect(url_for('delete_account'))
        
        try:
            # Delete all user's sessions and associated car data
            sessions = RaceSession.query.filter_by(user_id=current_user.id).all()
            for session in sessions:
                # Delete associated car data
                CarData.query.filter_by(session_id=session.id).delete()
                db.session.delete(session)
            
            # Delete all user's comparisons
            Comparison.query.filter_by(user_id=current_user.id).delete()
            
            # Delete the user account
            db.session.delete(current_user)
            db.session.commit()
            
            # Log out the user
            logout_user()
            
            flash('Your account has been permanently deleted.', 'info')
            return redirect(url_for('home'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting account: {str(e)}', 'error')
            return redirect(url_for('delete_account'))
    
    return render_template('delete_account.html', 
                         session_count=session_count, 
                         comparison_count=comparison_count)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not bcrypt.check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('change_password'))
        
        # Validate new password
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return redirect(url_for('change_password'))
        
        if not any(c.isupper() for c in new_password):
            flash('New password must contain at least one uppercase letter.', 'error')
            return redirect(url_for('change_password'))
        
        if not any(c.islower() for c in new_password):
            flash('New password must contain at least one lowercase letter.', 'error')
            return redirect(url_for('change_password'))
        
        if not any(c.isdigit() for c in new_password):
            flash('New password must contain at least one number.', 'error')
            return redirect(url_for('change_password'))
        
        # Check password confirmation
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('change_password'))
        
        # Check if new password is different from current
        if bcrypt.check_password_hash(current_user.password, new_password):
            flash('New password must be different from your current password.', 'error')
            return redirect(url_for('change_password'))
        
        try:
            # Update password
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            
            flash('Password updated successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating password: {str(e)}', 'error')
            return redirect(url_for('change_password'))
    
    return render_template('change_password.html')

def send_notification_email(user, subject, message):
    """Send email notification to user"""
    if not MAIL_AVAILABLE or not mail:
        print(f"Email not available. Would send to {user.email}: {subject}\n{message}")
        return
    
    if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
        try:
            msg = Message(subject, recipients=[user.email])
            msg.body = message
            mail.send(msg)
            print(f"Email sent to {user.email}: {subject}")
        except Exception as e:
            print(f"Error sending email: {e}")
    else:
        print(f"Email not configured. Would send to {user.email}: {subject}\n{message}")

def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

