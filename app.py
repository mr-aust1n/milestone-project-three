from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_paginate import Pagination, get_page_args
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_SENDER = os.getenv("MAILGUN_SENDER")

def send_email(to, subject, body):
    """ Sends an email using Mailgun API """
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Support System <{MAILGUN_SENDER}>",
            "to": to,
            "subject": subject,
            "text": body,
        }
    )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Submitted')

    # --- Admin Questions and User Responses ---
    admin_question = db.Column(db.Text, nullable=True)  # Admin’s question to user
    user_response = db.Column(db.Text, nullable=True)  # User’s reply to admin
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('tickets', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'warning')
            return redirect(url_for('register'))

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        # Send welcome email
        send_email(
            email,
            "Welcome to the Support System",
            f"Hello {email},\n\nYour account has been successfully created.\n\nThanks,\nSupport Team"
        )

        flash('Registration successful! Please check your email.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/submit_ticket', methods=['GET', 'POST'])
@login_required
def submit_ticket():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']

        new_ticket = Ticket(user_id=current_user.id, category=category, description=description)
        db.session.add(new_ticket)
        db.session.commit()

        # Define which admin(s) should receive ticket notifications from our website 
        category_admins = {
            "Email Support": ["emails@craigaust.in"],
            "Website Support": ["web@craigaust.in"],
            "Access Support": ["access@craigaust.in"],
            "QuickBooks Support": ["quickbooks@craigaust.in"],
            "Social Media Post": ["socials@craigaust.in"],
            "Other": ["misc@craigaust.in"]
        }

        assigned_admin_emails = category_admins.get(category, ["default_admin@craigaust.in"])

        send_email(
            assigned_admin_emails,
            "New Support Ticket Assigned",
            f"A new ticket has been submitted in your category:\n\nCategory: {category}\nDescription: {description}\n\nPlease log in to view the ticket."
        )

        flash('Your support ticket has been submitted!', 'success')
        return redirect(url_for('index'))

    return render_template('submit_ticket.html')

@app.route('/admin/question/<int:ticket_id>', methods=['POST'])
@login_required
def admin_question(ticket_id):
    if not current_user.is_admin:
        flash("Access Denied.", "danger")
        return redirect(url_for('admin_tickets'))

    ticket = Ticket.query.get_or_404(ticket_id)
    question = request.form.get('question')

    if question:
        ticket.admin_question = question
        ticket.status = "In Progress"
        db.session.commit()

        # Notify user
        send_email(
            ticket.user.email,
            "New Question from Admin",
            f"An admin has asked you a question regarding your support ticket:\n\n{question}\n\nPlease log in to reply."
        )

        flash("Question sent to user.", "success")

    return redirect(url_for('admin_tickets'))

@app.route('/user/response/<int:ticket_id>', methods=['POST'])
@login_required
def user_response(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.user_id != current_user.id:
        flash("Access Denied.", "danger")
        return redirect(url_for('view_tickets'))

    response = request.form.get('response')
    if response:
        ticket.user_response = response
        db.session.commit()

        # Notify admin
        send_email(
            "default_admin@craigaust.in",
            "User Replied to Ticket",
            f"The user has responded to your question:\n\n{response}\n\nPlease log in to continue the conversation."
        )

        flash("Response sent to admin.", "success")

    return redirect(url_for('view_tickets'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
