from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
