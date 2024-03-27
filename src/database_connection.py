
def get_database_url():
    # Verbindungsparameter
    USERNAME = "se-project"
    PASSWORD = "se-project"
    HOST = "localhost"
    PORT = "5432"
    DATABASE = "postgres"
    # URL für SQL-Alchemy
    DATABASE_URL = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
    return DATABASE_URL