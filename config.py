import os

class Config:
    SECRET_KEY = os.urandom(24)  # Secure session key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False