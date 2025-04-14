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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return "Welcome to Medical Services App! <a href='/register'>Register</a> | <a href='/login'>Login</a>"

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
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Dashboard (Protected Page)
@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}! Welcome to your dashboard.'

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Run Flask App with Waitress (Instead of Gunicorn)
@app.route('/search')
def search():
    return render_template('search.html')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database
    serve(app, host='0.0.0.0', port=10000)  # Waitress Server