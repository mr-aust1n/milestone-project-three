import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///instance/support_db.db"
    )
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Correct debug setting
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
    MAILGUN_SENDER = os.getenv("MAILGUN_SENDER")
    MAILGUN_WEBHOOK_SECRET = os.getenv("MAILGUN_WEBHOOK_SECRET")
    MAILGUN_PUBLIC_KEY = os.getenv("MAILGUN_PUBLIC_KEY")
