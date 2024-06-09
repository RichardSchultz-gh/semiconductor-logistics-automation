from config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_database_url():
    """
    Gibt die Datenbank URL mit Config-Informationen zurück
    :return: Datenbank URL
    """
    return config.SQLALCHEMY_DATABASE_URI

# Datenbankverbindung herstellen
def database_connection():
    """
    Stellt eine Verbindung zur Datenbank her
    :return: Session
    """
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session_d = Session()
    return session_d

def database_disconnection(session_d):
    """
    Schließt die Verbindung zur Datenbank
    :param session_d: Session
    :return: None
    """
    session_d.close()