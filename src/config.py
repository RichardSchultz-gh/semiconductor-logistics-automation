# config.py
class Config:
    # Name der Applikation
    APP_NAME = "Frau Holle"
    # Datenbank Konfiguration
    USERNAME = "se-project"
    PASSWORD = "se-project"
    HOST = "localhost"
    PORT = "5432"
    DATABASE = "postgres"
    SQLALCHEMY_DATABASE_URI = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
    
    # Konfiguration für die Anwendung
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = "Holle"

    # Login-Informationen für user1 und user2
    USER1 = "user1"
    PASSWORD_USER1 = "pass1"
    USER2 = "user2"
    PASSWORD_USER2 = "pass2"

config = Config()



