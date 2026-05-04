from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from extensions import db, bcrypt, mail
from models.models import User
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

auth = Blueprint('auth', __name__)

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECRET_KEY'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECRET_KEY'],
            max_age=expiration
        )
    except:
        return False
    return email

import requests
import os

def send_email(to, subject, template, confirm_url=None):
    api_key = current_app.config.get('MAIL_PASSWORD')
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')
    
    # Check if we should use Brevo's HTTP API instead of SMTP
    if api_key and (api_key.startswith('xsmtpsib-') or api_key.startswith('xkeysib-')):
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        payload = {
            "sender": {"email": sender_email},
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": template
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201, 202]:
                return True
            else:
                print(f"Brevo API Error: {response.text}")
                return False
        except Exception as e:
            print(f"Brevo API Exception: {e}")
            return False

    # Fallback to standard SMTP
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=sender_email
    )
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists. Please login.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        # is_verified is False by default
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password, is_verified=False)
        db.session.add(new_user)
        db.session.commit()
        
        token = generate_confirmation_token(new_user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url, first_name=new_user.first_name)
        print(f"\n\n*** CONFIRMATION LINK: {confirm_url} ***\n\n")
        subject = "Please confirm your email - AI CV Analyzer"
        success = send_email(new_user.email, subject, html, confirm_url=confirm_url)
        
        if not success:
            db.session.delete(new_user)
            db.session.commit()
            flash('Failed to send verification email. Please contact support or try again later.', 'danger')
            return redirect(url_for('auth.register'))
            
        flash('A confirmation email has been sent to your inbox. Please check your email to confirm and login.', 'success')
            
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Please verify your email address before logging in.', 'warning')
                return redirect(url_for('auth.login'))
                
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
