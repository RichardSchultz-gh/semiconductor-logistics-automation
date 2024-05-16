from config import config
def get_database_url():
    return config.SQLALCHEMY_DATABASE_URI