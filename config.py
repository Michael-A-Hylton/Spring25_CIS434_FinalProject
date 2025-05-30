import os

class Config:
    SECRET_KEY = os.urandom(24)  # Secure session key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  # or your SMTP provider
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'sms.2fa.verify@gmail.com'
    MAIL_PASSWORD = 'ohze aydx fpwe gfpv'
    MAIL_DEFAULT_SENDER = 'sms.2fa.verify@gmail.com'