from flask_sqlalchemy import SQLAlchemy
import re
import datetime
from email.utils import parseaddr
from flask_jwt_extended import create_access_token, create_refresh_token
from validate_email import validate_email


database = SQLAlchemy()

user_role_table = database.Table(
    'user_role',
    database.Column('user_id', database.Integer, database.ForeignKey('user.id'), primary_key=True),
    database.Column('role_id', database.Integer, database.ForeignKey('role.id'), primary_key=True)
)


class User(database.Model):
    __tablename__ = "user"

    id = database.Column(database.Integer, primary_key=True)
    jmbg = database.Column(database.String(13), nullable=False, unique=True)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)

    roles = database.relationship("Role", secondary=user_role_table, backref="users")

    def __repr__(self):
        return self.email + ", " + self.forename + " " + self.surname

    @staticmethod
    def is_jmbg_valid(jmbg):
        print(jmbg)
        if not re.search("^\d{13}$", jmbg):
            return False
        print("T1")
        day = int(jmbg[0:2])
        month = int(jmbg[2:4])
        year = int(jmbg[4:7])
        region = int(jmbg[7:9])
        unique_number = int(jmbg[9:12])
        checksum = int(jmbg[12:13])

        try:
            datetime.datetime(year, month, day)
        except ValueError:
            return False

        if region < 70 or region > 99:
            return False

        if unique_number < 0 or unique_number > 999:
            return False

        digits = [int(digit) for digit in jmbg]

        tmp = 0
        for i in range(0, 6):
            tmp += (7 - i) * (digits[i] + digits[i + 6])

        check = 11 - (tmp % 11)

        if check == 10 or check == 11:
            check = 0
        if checksum != check:
            return False

        return True

    @staticmethod
    def is_email_valid(email):
        # print("T", email, validate_email(email))
        # return parseaddr('foo@example.com')[1] != ""
        try:
            return email == "admin@admin.com" or validate_email(email, check_mx=True)
        except Exception:
            return False

    @staticmethod
    def is_password_valid(password):
        if len(password) < 8:
            return False

        if not re.search("[0-9]+", password):
            return False

        if not re.search("[a-z]+", password):
            return False

        if not re.search("[A-Z]+", password):
            return False

        return True

    @staticmethod
    def register_user(jmbg, forename, surname, email, password):
        database.session.begin()

        if jmbg == "":
            database.session.rollback()
            return "Field jmbg is missing.", 400
        if forename == "":
            database.session.rollback()
            return "Field forename is missing.", 400
        if surname == "":
            database.session.rollback()
            return "Field surname is missing.", 400
        if email == "":
            database.session.rollback()
            return "Field email is missing.", 400
        if password == "":
            database.session.rollback()
            return "Field password is missing.", 400

        if not User.is_jmbg_valid(jmbg):
            database.session.rollback()
            return "Invalid jmbg.", 400

        if not User.is_email_valid(email):
            database.session.rollback()
            return "Invalid email.", 400

        if not User.is_password_valid(password):
            database.session.rollback()
            return "Invalid password.", 400

        if User.query.filter(User.email == email).all():
            database.session.rollback()
            return "Email already exists.", 400

        new_user = User(
            jmbg=jmbg,
            forename=forename,
            surname=surname,
            email=email,
            password=password
        )
        new_user.roles.append(Role.query.filter(Role.name == "election_official").first())

        database.session.add(new_user)
        database.session.commit()
        return "", 200

    @staticmethod
    def login_user(email, password):

        if email == "":
            return None, None, "Field email is missing.", 400

        if password == "":
            return None, None, "Field password is missing.", 400

        if not User.is_email_valid(email):
            return None, None, "Invalid email.", 400

        user = User.query.filter(User.email == email).first()
        if not user or user.password != password:
            return None, None, "Invalid credentials.", 400

        additional_claims = {
            "jmbg": user.jmbg,
            "forename": user.forename,
            "surname": user.surname,
            "roles": [str(role) for role in user.roles],
        }

        access_token = create_access_token(identity=email, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=email, additional_claims=additional_claims)

        return access_token, refresh_token, None, 200

    @staticmethod
    def delete_user(email):
        if email == "":
            return "Field email is missing.", 400

        if not User.is_email_valid(email):
            return "Invalid email.", 400

        database.session.begin()

        user = User.query.filter(User.email == email).first()
        if not user:
            return "Unknown user.", 400

        database.session.delete(user)
        database.session.commit()

        return "", 200


class Role(database.Model):
    __tablename__ = "role"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)

    def __repr__(self):
        return self.name
