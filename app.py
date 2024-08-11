import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, request, session, redirect, url_for
from mock import mock_database_connection
from flask_bcrypt import Bcrypt

# Currently following tutorial from this:
# https://tutorial101.blogspot.com/2021/04/python-flask-postgresql-login-register.html
# https://www.youtube.com/watch?v=xIiNYn0q1gs

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")
bcrypt = Bcrypt()

USE_MOCK_DB = os.getenv("USE_MOCK_DB", "False") == "True"

if USE_MOCK_DB:
    # Use the mock database connection
    conn = mock_database_connection()
    print("Using mocked database connection.")
else:
    url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(url)
    print("Using real database connection.")


@app.route("/")
def home():
    # First need to check if user is logged in
    # originally had session["loggedin"], but loggedin might not be defined!
    if session.get("loggedin", False):
        return "You are in my dude!"

    # Otherwise, re-direct them to the login page:
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    print("this is request.form")
    print(request.form)

    if request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]

        # Check if the account exists in PostgreSQL:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        account = cursor.fetchone()

        if account:
            # Compare the hashed password
            if bcrypt.check_password_hash(account["password"], password):
                session["loggedin"] = True
                session["username"] = account["username"]

                # Redirect to home page:
                return redirect(url_for("home"))

            # Account not found, tell them to fk off:
            return "<h1>You're asking for teh wrong guy</h1>"

    # Load login template here
    return "<h1>Who the fak are you</h1>"


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# Checkout how "cursor" works: https://www.youtube.com/watch?v=eEikNXAsx20
@app.route("/blogs", methods=["GET", "POST"])
def blogs():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # First need to check if user is logged in
    if session["loggedin"]:

        # Fetch username
        username = session["username"]

        if request.method == "GET":
            # Check if the account exists in PostgreSQL:
            cursor.execute("SELECT * FROM blogs WHERE username = %s", (username))
            user_blogs = cursor.fetchall()
            return "<h2>{user_blogs}</h2>"

        elif request.method == "POST":
            pass
        else:
            # Need to return 404 error code
            return "<h1>Not a valid method!!!!!</h1>"

    # If user is not logged in, re-direct to login page:
    return redirect(url_for("login"))


# # TEMPORARY cursor testing
# cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# cursor.execute("SELECT * FROM users WHERE username = %s", ("kangerdrew",))
# account = cursor.fetchall()
# print(account)

if __name__ == "__main__":
    app.run(debug=True)
