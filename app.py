import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, request, session, redirect, url_for
from mock import mock_database_connection
from flask_bcrypt import Bcrypt

load_dotenv()

app = Flask(__name__)

USE_MOCK_DB = os.getenv("USE_MOCK_DB", 'False') == 'True'

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
    if "loggedin" in session:
        return "You are in my dude!"

    # Otherwise, re-direct them to the login page:
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Check if the account exists in PostgreSQL:
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
        else:

            return "<h1>You're asking for teh wrong guy</h1>"

    # Load login template here
    return "<h1>Who the fak are you</h1>"


if __name__ == "__main__":
    app.run(debug=True)
