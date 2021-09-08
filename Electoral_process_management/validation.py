from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import make_response, jsonify


def role_check(role):
    def inner_role(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                return make_response(jsonify(msg="Missing Authorization Header"), 401)
            claims = get_jwt()
            if "roles" in claims and role in claims["roles"]:
                return function(*args, **kwargs)
            else:
                return make_response(jsonify(msg="Missing Authorization Header"), 401)
        return decorator
    return inner_role
