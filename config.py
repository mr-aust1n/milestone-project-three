import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Core Flask config
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Use DATABASE_URL (Heroku) or fallback to local SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///instance/support_db.db'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Automatically disable debug in production
    DEBUG = os.getenv('FLASK_ENV') != 'production'

    # Optional: Mailgun settings
    MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
    MAILGUN_SENDER = os.getenv('MAILGUN_SENDER')
    MAILGUN_WEBHOOK_SECRET = os.getenv('MAILGUN_WEBHOOK_SECRET')
    MAILGUN_PUBLIC_KEY = os.getenv('MAILGUN_PUBLIC_KEY')
