from flask import Flask, request, session, redirect, url_for, flash, get_flashed_messages
import bcrypt
import threading
import json
import os
import datetime
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

USER_FILE = 'users.json'

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Change this in production!

    def load_users():
        if not os.path.exists(USER_FILE):
            return {}
        with open(USER_FILE, 'r') as f:
            return json.load(f)

    def save_users(users):
        with open(USER_FILE, 'w') as f:
            json.dump(users, f)

    def get_alerts():
        messages = get_flashed_messages(with_categories=True)
        alert_html = ""
        for category, message in messages:
            alert_html += f'''
            <div class="alert alert-{category} alert-dismissible fade show" role="alert">
                {message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            '''
        return alert_html

    def get_base_template(title, content):
        return f'''
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="light">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - Secure Portal</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/animate.css@4.1.1/animate.min.css">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css">
            <link rel="stylesheet" href="/static/css/style.css">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <meta name="theme-color" content="#2c3e50">
        </head>
        <body>
            <div class="cursor"></div>
            <div class="cursor-dot"></div>
            <div class="animated-bg"></div>
            <div class="progress-indicator"></div>
            
            <nav class="navbar navbar-expand-lg navbar-dark glass-card">
                <div class="container">
                    <a class="navbar-brand" href="/">
                        <i class="bi bi-shield-lock-fill me-2"></i>Secure Portal
                    </a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item">
                                <button class="btn btn-link nav-link" id="themeToggle" title="Toggle Dark Mode">
                                    <i class="bi bi-moon-fill"></i>
                                </button>
                            </li>
                            {'<li class="nav-item"><a class="nav-link" href="/logout" title="Sign Out"><i class="bi bi-box-arrow-right fs-5"></i></a></li>' if 'username' in session else ''}
                        </ul>
                    </div>
                </div>
            </nav>
            <main class="py-5 page-transition">
                {content}
            </main>
            <footer class="text-center py-4 text-muted glass-card">
                <div class="container">
                    <small>&copy; {datetime.datetime.now().year} Secure Portal. All rights reserved.</small>
                </div>
            </footer>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/toastify-js"></script>
            <script src="/static/js/main.js"></script>
        </body>
        </html>
        '''

    @app.route('/')
    def home():
        if 'username' in session:
            return redirect(url_for('welcome'))
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username'].strip()
            email = request.form['email'].strip()
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            users = load_users()
            if username in users:
                flash('Username already exists. Try another one.', 'danger')
                return redirect(url_for('register'))

            if len(password) < 6:
                flash('Password must be at least 6 characters.', 'warning')
                return redirect(url_for('register'))

            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('register'))

            if '@' not in email or '.' not in email:
                flash('Please enter a valid email address.', 'warning')
                return redirect(url_for('register'))

            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            users[username] = {
                'email': email,
                'hashed': hashed,
                'salt': salt.decode('utf-8')
            }
            save_users(users)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        content = f'''
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow p-4">
                        <div class="text-center mb-4">
                            <i class="bi bi-person-plus-fill welcome-icon"></i>
                            <h2 class="mb-3">Create Account</h2>
                            <p class="text-muted">Join our secure platform today</p>
                        </div>
                        {get_alerts()}
                        <form method="post">
                            <div class="form-floating mb-3">
                                <input name="username" class="form-control" id="username" placeholder="Username" required>
                                <label for="username"><i class="bi bi-person me-2"></i>Username</label>
                            </div>
                            <div class="form-floating mb-3">
                                <input name="email" type="email" class="form-control" id="email" placeholder="Email" required>
                                <label for="email"><i class="bi bi-envelope me-2"></i>Email</label>
                            </div>
                            <div class="form-floating mb-3">
                                <input name="password" type="password" class="form-control" id="password" 
                                    placeholder="Password" required minlength="6">
                                <label for="password"><i class="bi bi-key me-2"></i>Password</label>
                            </div>
                            <div class="form-floating mb-4">
                                <input name="confirm_password" type="password" class="form-control" id="confirm_password" 
                                    placeholder="Confirm Password" required>
                                <label for="confirm_password"><i class="bi bi-key-fill me-2"></i>Confirm Password</label>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 mb-3">
                                <i class="bi bi-person-plus me-2"></i>Create Account
                            </button>
                        </form>
                        <p class="text-center mt-3">Already have an account? 
                            <a href="/login" class="text-decoration-none fw-bold">Login here</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
        '''
        return get_base_template('Register', content)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username'].strip()
            password = request.form['password']
            users = load_users()
            user = users.get(username)
            if user:
                salt = user['salt'].encode('utf-8')
                hashed_input = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                if hashed_input == user['hashed']:
                    session['username'] = username
                    flash('Login successful!', 'success')
                    return redirect(url_for('welcome'))
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

        content = f'''
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow p-4">
                        <div class="text-center mb-4">
                            <i class="bi bi-box-arrow-in-right welcome-icon"></i>
                            <h2 class="mb-3">Welcome Back</h2>
                            <p class="text-muted">Sign in to your account</p>
                        </div>
                        {get_alerts()}
                        <form method="post">
                            <div class="form-floating mb-3">
                                <input name="username" class="form-control" id="username" placeholder="Username" required>
                                <label for="username"><i class="bi bi-person me-2"></i>Username</label>
                            </div>
                            <div class="form-floating mb-4">
                                <div class="input-group">
                                    <input name="password" type="password" class="form-control" id="password" 
                                        placeholder="Password" required>
                                    <span class="input-group-text password-toggle">
                                        <i class="bi bi-eye"></i>
                                    </span>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-success w-100 mb-3">
                                <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
                            </button>
                        </form>
                        <p class="text-center mt-3">
                            <a href="/register" class="text-decoration-none fw-bold">Register here</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
        '''
        return get_base_template('Login', content)

    @app.route('/welcome')
    def welcome():
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']
        users = load_users()
        email = users[username]['email']
        
        content = f'''
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card welcome-card">
                        <div class="text-center">
                            <i class="bi bi-person-circle welcome-icon"></i>
                            <h2 class="mb-3">Welcome, {username}!</h2>
                            <p class="lead mb-4">
                                <i class="bi bi-envelope me-2"></i>{email}
                            </p>
                            <a href="/logout" class="btn btn-outline-danger">
                                <i class="bi bi-box-arrow-right me-2"></i>Sign Out
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        return get_base_template('Welcome', content)

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        flash('Signed out successfully.', 'info')
        return redirect(url_for('login'))

    return app

def run_http():
    app_http = create_app()
    app_http.run(host='0.0.0.0', port=80)

def run_https():
    from flask_talisman import Talisman
    app_https = create_app()
    Talisman(app_https, content_security_policy=None)
    context = ('server.crt', 'server.key')
    app_https.run(host='0.0.0.0', port=443, ssl_context=context)

if __name__ == '__main__':
    # Make sure users.json exists
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({}, f)

    from threading import Thread

    # Run HTTP on port 5000 (dev-friendly, no warnings)
    def run_http():
        app = create_app()
        app.run(host='0.0.0.0', port=5000)

    # Run HTTPS on port 443 (self-signed SSL)
    def run_https():
        app = create_app()
        from flask_talisman import Talisman
        Talisman(app, content_security_policy=None)
        context = ('server.crt', 'server.key')
        app.run(host='0.0.0.0', port=443, ssl_context=context)

    print("Starting Secure Portal on HTTP 5000 & HTTPS 443...")

    Thread(target=run_http, daemon=True).start()
    Thread(target=run_https, daemon=True).start()

    # KEEP PROCESS ALIVE (no crash, no join required)
    while True:
        pass

