import os


class Configuration:
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{os.environ.get('DATABASE_URL')}/election_database"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    REDIS_VOTE_LIST = "votes"
    if os.environ.get('REDIS_URL'):
        REDIS_HOST = os.environ.get('REDIS_URL')
