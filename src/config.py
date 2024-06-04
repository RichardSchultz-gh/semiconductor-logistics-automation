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

    # Login-Informationen:
    #user1: Fertigungsleiter
    USER1 = "user1"
    PASSWORD_USER1 = "pass1"
    #user2: Mitarbeiter
    USER2 = "user2"
    PASSWORD_USER2 = "pass2"

config = Config()



