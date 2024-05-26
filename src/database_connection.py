from config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_database_url():
    return config.SQLALCHEMY_DATABASE_URI

# Datenbankverbindung herstellen
def database_connection():
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session_d = Session()
    return session_d

def database_disconnection(session_d):
    session_d.close()