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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/submit_ticket', methods=['GET', 'POST'])
@login_required
def submit_ticket():
    if request.method == 'POST':
        category = request.form.get('category')
        description = request.form.get('description')

        # Ensure category and description are not empty
        if not category or not description.strip():
            flash('Category and description are required.', 'danger')
            return redirect(url_for('submit_ticket'))

        # Create new ticket
        new_ticket = Ticket(user_id=current_user.id, category=category, description=description, status="Submitted")
        db.session.add(new_ticket)
        db.session.commit()

        # Notify the correct admins
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
            f"A new support ticket has been submitted:\n\n"
            f"**Category:** {category}\n"
            f"**Description:** {description}\n\n"
            f"Please log in to view and respond to the ticket."
        )

        flash('Your support ticket has been submitted successfully!', 'success')
        return redirect(url_for('view_tickets'))

    return render_template('submit_ticket.html')
    

@app.route('/edit_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # Allow admins to edit any ticket, but users can only edit their own tickets
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash("Access Denied. You can only edit your own tickets.", "danger")
        return redirect(url_for('view_tickets'))

    if request.method == 'POST':
        category = request.form.get('category')
        description = request.form.get('description')

        if not category or not description.strip():
            flash('Category and description are required.', 'danger')
            return redirect(url_for('edit_ticket', ticket_id=ticket.id))

        ticket.category = category
        ticket.description = description
        db.session.commit()

        flash("Ticket updated successfully!", "success")
        return redirect(url_for('view_tickets'))

    return render_template('edit_ticket.html', ticket=ticket)

@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # Users can only delete their own "Submitted" tickets
    if not current_user.is_admin:
        if ticket.user_id != current_user.id:
            flash("You don't have permission to delete this ticket.", "danger")
            return redirect(url_for('view_tickets'))
        if ticket.status != "Submitted":
            flash("You can only delete tickets that are still 'Submitted'.", "warning")
            return redirect(url_for('view_tickets'))

    db.session.delete(ticket)
    db.session.commit()
    flash("Ticket deleted successfully.", "success")

    if current_user.is_admin:
        return redirect(url_for('admin_tickets'))
    return redirect(url_for('view_tickets'))


@app.route('/tickets', methods=['GET'])
@login_required
def view_tickets():
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status_filter', '')

    tickets_query = Ticket.query.filter_by(user_id=current_user.id)

    if search_query:
        tickets_query = tickets_query.filter(
            Ticket.category.ilike(f"%{search_query}%") |
            Ticket.description.ilike(f"%{search_query}%")
        )

    if status_filter:
        tickets_query = tickets_query.filter_by(status=status_filter)

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 5
    total = tickets_query.count()
    tickets = tickets_query.offset(offset).limit(per_page).all()

    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('tickets.html', tickets=tickets, pagination=pagination)

@app.route('/mark_done/<int:ticket_id>')
@login_required
def mark_done(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if not current_user.is_admin:
        flash("You don't have permission to mark this ticket as done.", "danger")
        return redirect(url_for('view_tickets'))

    ticket.status = "Done"
    db.session.commit()
    flash("Ticket marked as Done!", "success")
    
    return redirect(url_for('view_tickets'))


# Adding in progress status
@app.route('/update_status/<int:ticket_id>', methods=['POST'])
@login_required
def update_status(ticket_id):
    if not current_user.is_admin:
        flash("Access Denied: Admins only.", "danger")
        return redirect(url_for('index'))

    ticket = Ticket.query.get_or_404(ticket_id)
    new_status = request.form.get('status')

    if new_status not in ["Submitted", "In Progress", "On Hold", "Done"]:
        flash("Invalid status update.", "danger")
        return redirect(url_for('admin_tickets'))

    ticket.status = new_status
    db.session.commit()

    # Sends email to the ticket owner (submitter)
    send_email(
        ticket.user.email,
        f"Your ticket status has been updated to '{new_status}'",
        f"Hi {ticket.user.email},\n\n"
        f"Your support ticket (ID: {ticket.id}) has been updated by an admin.\n\n"
        f"New Status: {new_status}\n"
        f"Category: {ticket.category}\n"
        f"Description: {ticket.description}\n\n"
        f"Please log in to view more details.\n\n"
        f"Thanks,\nSupport Team"
    )

    flash(f"Ticket status updated to {new_status}.", "success")
    return redirect(url_for('admin_tickets'))


@app.route('/admin/tickets', methods=['GET'])
@login_required
def admin_tickets():
    if not current_user.is_admin:
        flash("Access Denied: Admins only.", "danger")
        return redirect(url_for('index'))

    search_query = request.args.get('search', '')
    status_filter = request.args.get('status_filter', '')

    tickets_query = Ticket.query

    if search_query:
        tickets_query = tickets_query.filter(
            Ticket.category.ilike(f"%{search_query}%") |
            Ticket.description.ilike(f"%{search_query}%")
        )

    if status_filter:
        tickets_query = tickets_query.filter_by(status=status_filter)

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 10
    total = tickets_query.count()
    tickets = tickets_query.offset(offset).limit(per_page).all()

    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('admin_tickets.html', tickets=tickets, pagination=pagination)


# Dashboard for Admins
@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('index'))

    # Total tickets per category
    data = db.session.query(
        Ticket.category,
        db.func.count(Ticket.id)
    ).group_by(Ticket.category).all()

    categories = [row[0] for row in data]
    counts = [row[1] for row in data]

    # Admin category mapping
    category_admins = {
        "Email Support": ["emails@craigaust.in"],
        "Website Support": ["web@craigaust.in"],
        "Access Support": ["access@craigaust.in"],
        "QuickBooks Support": ["quickbooks@craigaust.in"],
        "Social Media Post": ["socials@craigaust.in"],
        "Other": ["misc@craigaust.in"]
    }

    # Build status-based ticket counts per admin
    statuses = ["Submitted", "In Progress", "On Hold", "Done"]
    admin_stats = {}  # {admin: {status: count}}

    for email in set(email for emails in category_admins.values() for email in emails):
        admin_stats[email] = {status: 0 for status in statuses}

    all_tickets = Ticket.query.all()
    for ticket in all_tickets:
        admins = category_admins.get(ticket.category, ["default_admin@craigaust.in"])
        for admin in admins:
            if ticket.status in statuses:
                admin_stats[admin][ticket.status] += 1

    # Transform for Chart.js
    admin_labels = list(admin_stats.keys())
    dataset_dict = {status: [] for status in statuses}

    for admin in admin_labels:
        for status in statuses:
            dataset_dict[status].append(admin_stats[admin][status])

    return render_template(
        'dashboard.html',
        categories=categories,
        counts=counts,
        admin_labels=admin_labels,
        dataset_dict=dataset_dict,
        statuses=statuses
    )


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
