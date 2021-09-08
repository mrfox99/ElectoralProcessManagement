import os
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import database_exists, create_database, drop_database

from configuration import Configuration
from Authentication.models import database
from Authentication.models import Role, User

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

            admin_role = Role(name="administrator")
            user_role = Role(name="election_official")

            database.session.add(admin_role)
            database.session.add(user_role)
            database.session.commit()

            admin = User(
                jmbg="0000000000000",
                forename="admin",
                surname="admin",
                email="admin@admin.com",
                password="1"
            )
            admin.roles.append(admin_role)

            database.session.add(admin)
            database.session.commit()

        done = True

    except Exception as error:
        print(error)
