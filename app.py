from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from waitress import serve  # Import Waitress for deployment

# Initialize Flask app
app = Flask(__name__)

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite for now
app.config['SECRET_KEY'] = 'your_secret_key'  # Security key

# Initialize database
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class MedicalService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('search'))
    return render_template('login.html')

# Dashboard (Protected Page)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Run Flask App with Waitress (Instead of Gunicorn)
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.args.get('query', '').lower()
    results = []

    if query:
        results = MedicalService.query.filter(
            (MedicalService.name.ilike(f"%{query}%")) |
            (MedicalService.location.ilike(f"%{query}%")) |
            (MedicalService.service_type.ilike(f"%{query}%"))
        ).all()

    return render_template('search.html', results=results, query=query)
@app.route('/add_sample_data')
def add_sample_data():
    sample_services = [
        MedicalService(name="Home Nurse for Wound Care", location="Hyderabad", service_type="nurse"),
        MedicalService(name="Oxygen Cylinder Setup", location="Vizag", service_type="oxygen"),
        MedicalService(name="Post-Surgery Scrub Nurse", location="Vijayawada", service_type="nurse"),
        MedicalService(name="Respiratory Technician", location="Bangalore", service_type="technician")
    ]
    db.session.add_all(sample_services)
    db.session.commit()
    return "Sample data added successfully!"
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database
    serve(app, host='0.0.0.0', port=10000)  # Waitress Server