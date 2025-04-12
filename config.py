import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super_secret_key"
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:cristian1234@localhost/retea_comunicare"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app\\static\\uploads')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'gabi.vladoiu1389@gmail.com'
    MAIL_PASSWORD = 'etzyclcjqycydrss'
    MAIL_DEFAULT_SENDER = 'gabi.vladoiu1389@gmail.com'