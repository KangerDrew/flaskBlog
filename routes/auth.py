from flask import Blueprint, request, session
from flask_bcrypt import Bcrypt
from connector import db_connect
from APIResponse import APIResponse

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

response_formatter = APIResponse()


@auth_bp.route("/")
def home():
    # First need to check if user is logged in
    # originally had session["loggedin"], but loggedin might not be defined!
    if session.get("loggedin", False):
        return response_formatter.generate_response_s("You are currently logged in."), 200

    # Otherwise, re-direct them to the login page:
    return response_formatter.generate_response_s("You are not that guy."), 200


@auth_bp.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    query = "SELECT * FROM \"user\" WHERE username = %s"
    params = (username,)
    account = db_connect(query, params)

    if account:
        # Compare the hashed password
        if bcrypt.check_password_hash(account["password"], password):
            session["loggedin"] = True
            session["username"] = account["username"]

            # Send back login confirmation result:
            return response_formatter.generate_response_s("Login successful!"), 200

    # Account not found, return error
    return response_formatter.generate_response_f("Account information not found."), 400


@auth_bp.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.clear()
    # Redirect to login page
    return response_formatter.generate_response_s("You are now logged out."), 200

