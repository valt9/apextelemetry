from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import json
import os
import csv
import io
from f1_api import F1API
try:
    from cryptography.fernet import Fernet
except Exception as e:
    raise RuntimeError("Missing dependency: 'cryptography' is required. Install with `python -m pip install -r requirements.txt` or `python -m pip install cryptography`.")
import hashlib
import hmac

# Encryption / HMAC helpers
def get_fernet():
    key = os.environ.get('FERNET_KEY')
    if not key:
        raise RuntimeError('FERNET_KEY environment variable is required for encrypting user data')
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)

def encrypt_value(value: str) -> bytes:
    if value is None:
        return None
    f = get_fernet()
    return f.encrypt(value.encode())

def decrypt_value(token: bytes) -> str:
    if token is None:
        return None
    f = get_fernet()
    return f.decrypt(token).decode()

def make_hmac(value: str) -> str:
    if value is None:
        return None
    key = os.environ.get('HMAC_KEY', os.environ.get('FERNET_KEY'))
    if not key:
        raise RuntimeError('HMAC_KEY or FERNET_KEY environment variable is required for deterministic lookup')
    if isinstance(key, str):
        key = key.encode()
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///apex_telemetry.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # Deterministic HMACs for lookup (unique constraints remain enforced here)
    username_hmac = db.Column(db.String(64), unique=True, nullable=False)
    email_hmac = db.Column(db.String(64), unique=True, nullable=False)

    # Encrypted blobs for the actual values (Fernet encrypted bytes)
    username_encrypted = db.Column(db.LargeBinary, nullable=False)
    email_encrypted = db.Column(db.LargeBinary, nullable=False)

    # Passwords remain hashed with bcrypt (non-reversible)
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def username(self):
        try:
            return decrypt_value(self.username_encrypted)
        except Exception:
            return None

    @username.setter
    def username(self, val: str):
        self.username_hmac = make_hmac(val)
        self.username_encrypted = encrypt_value(val)

    @property
    def email(self):
        try:
            return decrypt_value(self.email_encrypted)
        except Exception:
            return None

    @email.setter
    def email(self, val: str):
        self.email_hmac = make_hmac(val)
        self.email_encrypted = encrypt_value(val)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(140), nullable=False)
    driver = db.Column(db.String(140), nullable=True)
    team = db.Column(db.String(140), nullable=True)
    date = db.Column(db.String(40), nullable=True)
    data_json = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('sessions', lazy=True))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            flash('Please fill out all fields', 'warning')
            return redirect(url_for('register'))
        try:
            username_h = make_hmac(username)
            email_h = make_hmac(email)
        except Exception as e:
            flash('Server encryption not configured: ' + str(e), 'danger')
            return redirect(url_for('register'))

        existing = User.query.filter((User.username_hmac == username_h) | (User.email_hmac == email_h)).first()
        if existing:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))

        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User()
        user.username = username
        user.email = email
        user.password_hash = pw_hash
        db.session.add(user)
        db.session.commit()
        flash('Account created. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            username_h = make_hmac(username)
        except Exception as e:
            flash('Server encryption not configured: ' + str(e), 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username_hmac=username_h).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Placeholder sample data for charts (will be replaced by F1 API data later)
    sample = {
        'labels': ['Lap 1', 'Lap 2', 'Lap 3', 'Lap 4', 'Lap 5'],
        'speeds': [180, 185, 182, 186, 183],
        'rpms': [12000, 12150, 11950, 12200, 12050]
    }
    return render_template('dashboard.html', sample=sample)


@app.route('/f1-viewer')
@login_required
def f1_viewer():
    """Display the F1 telemetry viewer."""
    return render_template('f1_viewer.html')


@app.route('/sessions')
@login_required
def sessions_list():
    sessions = Session.query.filter_by(user_id=current_user.id).all()
    return render_template('sessions.html', sessions=sessions)


@app.route('/sessions/new', methods=['GET', 'POST'])
@login_required
def sessions_new():
    if request.method == 'POST':
        name = request.form.get('name')
        driver = request.form.get('driver')
        team = request.form.get('team')
        date = request.form.get('date')
        data = request.form.get('data')
        if not name:
            flash('Name is required', 'warning')
            return redirect(url_for('sessions_new'))
        s = Session(user_id=current_user.id, name=name, driver=driver, team=team, date=date, data_json=data)
        db.session.add(s)
        db.session.commit()
        flash('Session created', 'success')
        return redirect(url_for('sessions_list'))
    return render_template('session_form.html', action='Create', session=None)


@app.route('/sessions/<int:sid>/edit', methods=['GET', 'POST'])
@login_required
def sessions_edit(sid):
    s = Session.query.get_or_404(sid)
    if s.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('sessions_list'))
    if request.method == 'POST':
        s.name = request.form.get('name')
        s.driver = request.form.get('driver')
        s.team = request.form.get('team')
        s.date = request.form.get('date')
        s.data_json = request.form.get('data')
        db.session.commit()
        flash('Session updated', 'success')
        return redirect(url_for('sessions_list'))
    return render_template('session_form.html', action='Edit', session=s)


@app.route('/sessions/<int:sid>/delete', methods=['POST'])
@login_required
def sessions_delete(sid):
    s = Session.query.get_or_404(sid)
    if s.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('sessions_list'))
    db.session.delete(s)
    db.session.commit()
    flash('Session deleted', 'info')
    return redirect(url_for('sessions_list'))


# F1 API Routes
@app.route('/api/f1/meetings')
@login_required
def api_meetings():
    year = request.args.get('year', type=int)
    country = request.args.get('country')
    meetings = F1API.get_meetings(year=year, country_name=country)
    return jsonify(meetings)


@app.route('/api/f1/sessions')
@login_required
def api_sessions():
    meeting_key = request.args.get('meeting_key', type=int)
    sessions = F1API.get_sessions(meeting_key=meeting_key)
    return jsonify(sessions)


@app.route('/api/f1/drivers')
@login_required
def api_drivers():
    session_key = request.args.get('session_key', type=int)
    if not session_key:
        return jsonify({"error": "session_key required"}), 400
    drivers = F1API.get_drivers(session_key)
    return jsonify(drivers)


@app.route('/api/f1/car-data')
@login_required
def api_car_data():
    session_key = request.args.get('session_key', type=int)
    driver_number = request.args.get('driver_number', type=int)
    if not session_key:
        return jsonify({"error": "session_key required"}), 400
    car_data = F1API.get_car_data(session_key, driver_number)
    processed = F1API.process_car_data_for_charts(car_data)
    return jsonify(processed)


@app.route('/api/f1/lap-data')
@login_required
def api_lap_data():
    session_key = request.args.get('session_key', type=int)
    driver_number = request.args.get('driver_number', type=int)
    if not session_key:
        return jsonify({"error": "session_key required"}), 400
    lap_data = F1API.get_laps(session_key, driver_number)
    processed = F1API.process_lap_data_for_charts(lap_data)
    return jsonify(processed)


@app.route('/api/f1/position-data')
@login_required
def api_position_data():
    session_key = request.args.get('session_key', type=int)
    driver_number = request.args.get('driver_number', type=int)
    if not session_key:
        return jsonify({"error": "session_key required"}), 400
    position_data = F1API.get_position_data(session_key, driver_number)
    processed = F1API.process_position_data_for_charts(position_data)
    return jsonify(processed)


@app.route('/driver-comparison')
@login_required
def driver_comparison():
    """Display driver comparison view."""
    return render_template('driver_comparison.html')


@app.route('/sector-breakdown')
@login_required
def sector_breakdown():
    """Display sector breakdown view."""
    return render_template('sector_breakdown.html')


@app.route('/api/f1/compare-drivers')
@login_required
def api_compare_drivers():
    session_key = request.args.get('session_key', type=int)
    driver_1 = request.args.get('driver_1', type=int)
    driver_2 = request.args.get('driver_2', type=int)
    if not all([session_key, driver_1, driver_2]):
        return jsonify({"error": "session_key, driver_1, and driver_2 required"}), 400
    
    comparison_data = F1API.compare_drivers(session_key, driver_1, driver_2)
    return jsonify(comparison_data)


@app.route('/api/f1/sector-data')
@login_required
def api_sector_data():
    session_key = request.args.get('session_key', type=int)
    driver_number = request.args.get('driver_number', type=int)
    if not session_key:
        return jsonify({"error": "session_key required"}), 400
    lap_data = F1API.get_laps(session_key, driver_number)
    processed = F1API.process_sector_data(lap_data)
    return jsonify(processed)


@app.route('/api/export/telemetry')
@login_required
def export_telemetry():
    """Export telemetry data as CSV or JSON."""
    session_key = request.args.get('session_key', type=int)
    driver_number = request.args.get('driver_number', type=int)
    export_format = request.args.get('format', 'csv').lower()
    
    if not session_key:
        return jsonify({"error": "session_key required"}), 400
    
    # Fetch car data
    car_data = F1API.get_car_data(session_key, driver_number)
    
    if export_format == 'json':
        output = io.StringIO()
        json.dump(car_data, output, indent=2)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f"telemetry_{session_key}_{driver_number}.json"
        )
    else:  # csv
        if not car_data:
            return jsonify({"error": "No data found"}), 404
        
        output = io.StringIO()
        fieldnames = car_data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(car_data)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"telemetry_{session_key}_{driver_number}.csv"
        )


@app.route('/api/export/lap-data')
@login_required
def export_lap_data():
    """Export lap data as CSV or JSON."""
    session_key = request.args.get('session_key', type=int)
    driver_number = request.args.get('driver_number', type=int)
    export_format = request.args.get('format', 'csv').lower()
    
    if not session_key:
        return jsonify({"error": "session_key required"}), 400
    
    # Fetch lap data
    lap_data = F1API.get_laps(session_key, driver_number)
    
    if export_format == 'json':
        output = io.StringIO()
        json.dump(lap_data, output, indent=2)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f"laps_{session_key}_{driver_number}.json"
        )
    else:  # csv
        if not lap_data:
            return jsonify({"error": "No data found"}), 404
        
        output = io.StringIO()
        fieldnames = lap_data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lap_data)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"laps_{session_key}_{driver_number}.csv"
        )


if __name__ == '__main__':
    # Ensure DB exists
    with app.app_context():
        db.create_all()
    app.run(debug=True)
