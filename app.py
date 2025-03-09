from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
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
        
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        
        flash('Registration successful!', 'success')
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

@app.route('/tickets')
@login_required
def view_tickets():
    if current_user.is_authenticated:
        user_tickets = Ticket.query.filter_by(user_id=current_user.id).all()
        return render_template('tickets.html', tickets=user_tickets)

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

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
