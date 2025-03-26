import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Core Flask config
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optional: Automatically turn off DEBUG in production
    DEBUG = os.getenv('FLASK_ENV') != 'production'

    # Optional: Mailgun (can access via app.config if preferred)
    MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
    MAILGUN_SENDER = os.getenv('MAILGUN_SENDER')
    MAILGUN_WEBHOOK_SECRET = os.getenv('MAILGUN_WEBHOOK_SECRET')
    MAILGUN_PUBLIC_KEY = os.getenv('MAILGUN_PUBLIC_KEY')
