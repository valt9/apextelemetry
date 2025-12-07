from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apex_telemetry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

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
        existing = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=pw_hash)
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
        user = User.query.filter_by(username=username).first()
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


if __name__ == '__main__':
    # Ensure DB exists
    with app.app_context():
        db.create_all()
    app.run(debug=True)
