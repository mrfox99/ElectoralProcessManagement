from flask import request, Response, jsonify, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt, create_access_token

from Authentication import application
from Authentication.models import User


@application.route("/", methods=["GET"])
def index():
    print(User.query.first())
    return "Hello World"


@application.route("/register", methods=["POST"])
def register():
    if not request.json:
        return make_response(jsonify(message="Field jmbg is missing."), 400)

    jmbg = request.json.get("jmbg", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    message, status = User.register_user(
        jmbg=jmbg,
        forename=forename,
        surname=surname,
        email=email,
        password=password
    )
    if status == 200:
        return make_response("", status)
    else:
        return make_response(jsonify(message=message), status)


@application.route("/login", methods=["POST"])
def login():
    if not request.json:
        return make_response(jsonify(message="Field email is missing."), 400)

    email = request.json.get("email", "")
    password = request.json.get("password", "")

    access_token, refresh_token, message, status = User.login_user(
        email=email,
        password=password
    )

    if access_token and refresh_token:
        return make_response(jsonify(accessToken=access_token, refreshToken=refresh_token), status)
    else:
        return make_response(jsonify(message=message), status)


@application.route("/refresh", methods=["POST"])
def refresh():
    try:
        verify_jwt_in_request(refresh=True)
        identity = get_jwt_identity()
        refresh_claims = get_jwt()
        additional_claims = {
            "jmbg": refresh_claims["jmbg"],
            "forename": refresh_claims["forename"],
            "surname": refresh_claims["surname"],
            "roles": refresh_claims["roles"]
        }
        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        return make_response(jsonify(accessToken=access_token), 200)

    except Exception:
        return make_response(jsonify(msg="Missing Authorization Header"), 401)


@application.route("/delete", methods=["POST"])
def delete():
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        if not ("roles" in claims and "administrator" in claims["roles"]):
            raise Exception()

        if not request.json:
            return make_response(jsonify(message="Field email is missing."), 400)

        email = request.json.get("email", "")
        message, status = User.delete_user(email=email)
        if status == 200:
            return make_response("", 200)
        else:
            return make_response(jsonify(message=message), 400)

    except Exception:
        return make_response(jsonify(msg="Missing Authorization Header"), 401)
