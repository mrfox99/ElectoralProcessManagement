from datetime import timedelta
import os


class Configuration:
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{os.environ.get('DATABASE_URL')}/election_database"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
