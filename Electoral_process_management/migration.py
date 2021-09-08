import os
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import database_exists, create_database, drop_database

from models import database
from configuration import Configuration

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)

done = False

while not done:

    try:

        if database_exists(Configuration.SQLALCHEMY_DATABASE_URI):
            drop_database(Configuration.SQLALCHEMY_DATABASE_URI)
        create_database(Configuration.SQLALCHEMY_DATABASE_URI)

        migrate_ = Migrate(application, database)

        with application.app_context() as context:

            if os.environ["INITIALIZATION"] == "True":
                init()
                migrate(message="Production migration.")
            upgrade()

        done = True

    except Exception as error:
        print(error)
