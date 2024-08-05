import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, session, redirect, url_for
from mock import mock_database_connection

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
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Check if the account exists in PostgreSQL:


    return "Login beawhwe"


if __name__ == "__main__":
    app.run(debug=True)
