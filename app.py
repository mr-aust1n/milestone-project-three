from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_paginate import Pagination, get_page_args
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Admin column

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

        # Validate if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        # Enforce Strong Password Policy
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'warning')
            return redirect(url_for('register'))

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        flash('Registration successful! Please log in.', 'success')
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
        category = request.form['category']
        description = request.form['description']

        new_ticket = Ticket(user_id=current_user.id, category=category, description=description)
        db.session.add(new_ticket)
        db.session.commit()

        flash('Your support ticket has been submitted!', 'success')
        return redirect(url_for('index'))

    return render_template('submit_ticket.html')

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

    # Pagination setup for users only
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 5  # Show 5 tickets per page for users admin get 10 See below.
    total = tickets_query.count()
    tickets = tickets_query.offset(offset).limit(per_page).all()

    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('tickets.html', tickets=tickets, pagination=pagination)

@app.route('/edit_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.user_id != current_user.id:
        flash("You don't have permission to edit this ticket.", "danger")
        return redirect(url_for('view_tickets'))

    if request.method == 'POST':
        ticket.category = request.form['category']
        ticket.description = request.form['description']
        db.session.commit()
        flash("Ticket updated successfully!", "success")
        return redirect(url_for('view_tickets'))

    return render_template('edit_ticket.html', ticket=ticket)

@app.route('/mark_done/<int:ticket_id>')
@login_required
def mark_done(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # Only allow admins to mark tickets as Done
    if not current_user.is_admin:
        flash("You don't have permission to mark this ticket as done.", "danger")
        return redirect(url_for('view_tickets'))

    ticket.status = "Done"
    db.session.commit()
    flash("Ticket marked as Done!", "success")
    
    return redirect(url_for('view_tickets'))

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

    # Pagination setup for admins
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 10  # Show 10 tickets per page for admins only
    total = tickets_query.count()
    tickets = tickets_query.offset(offset).limit(per_page).all()

    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('admin_tickets.html', tickets=tickets, pagination=pagination)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
