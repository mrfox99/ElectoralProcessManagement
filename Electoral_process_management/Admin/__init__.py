from flask import Flask
from flask_jwt_extended import JWTManager

from models import database
from configuration import Configuration

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)
jwt = JWTManager(application)

from Admin import routes
