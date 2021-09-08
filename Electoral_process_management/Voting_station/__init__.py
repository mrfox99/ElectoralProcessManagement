from flask import Flask
from flask_jwt_extended import JWTManager

from configuration import Configuration

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

from Voting_station import routes
