import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, request, session, redirect, url_for, render_template
from mock import mock_database_connection
from flask_bcrypt import Bcrypt
from datetime import datetime

# Currently following tutorial from this:
# https://tutorial101.blogspot.com/2021/04/python-flask-postgresql-login-register.html
# https://www.youtube.com/watch?v=xIiNYn0q1gs

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")
bcrypt = Bcrypt(app)

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
        return render_template("home.html")

    # Otherwise, re-direct them to the login page:
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Check if the account exists in PostgreSQL:
            cursor.execute("SELECT * FROM \"user\" WHERE username = %s", (username,))
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
    return render_template("login.html")


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.clear()
    # Redirect to login page
    return redirect(url_for('login'))


# Checkout how "cursor" works: https://www.youtube.com/watch?v=eEikNXAsx20
@app.route("/blog", methods=["GET", "POST", "PUT"])
def blog():

    # First need to check if user is logged in
    if session.get("loggedin", False):

        # Fetch username
        username = session["username"]

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

            if request.method == "GET":

                username = session["username"]
                cursor.execute("SELECT * FROM blog WHERE username = %s", (username,))

                # TODO: Also retrieve category information pertaining to the blogs!!

                all_blogs = cursor.fetchall()
                return render_template("blog.html", blogs=all_blogs)

            elif request.method == "POST":
                # Create a new blog post
                title = request.form["title"]
                content = request.form["content"]
                current_t = datetime.now()

                cursor.execute("INSERT INTO blog (username, title, content, created_at) VALUES (%s, %s, %s, %s)",
                               (username, title, content, current_t))
                conn.commit()
                return redirect(url_for("blog"))

            elif request.method == "PUT":
                # Update an existing blog post
                blog_id = request.form["blog_id"]
                new_content = request.form["content"]
                cursor.execute("UPDATE blog SET content = %s WHERE id = %s AND username = %s",
                               (new_content, blog_id, username))
                conn.commit()
                return redirect(url_for("blog"))

    # If user is not logged in, re-direct to login page:
    return redirect(url_for("login"))


@app.route("/blog/<int:blog_id>", methods=["DELETE"])
def delete_blog(blog_id):

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

        if not session.get("loggedin"):
            return redirect(url_for("login"))

        username = session["username"]
        cursor.execute("DELETE FROM blog WHERE blog_id = %s AND username = %s", (blog_id, username))
        conn.commit()
        return "", 204  # Return 204 No Content


# # TEMPORARY cursor testing
# cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# cursor.execute("SELECT * FROM blog_category WHERE blog_id = %s", ("1",))
# stuff = cursor.fetchall()
# print(type(stuff[0][0]))
# print(stuff)
#
# cursor.execute("SELECT * FROM user")
# account = cursor.fetchall()
# print(account)


if __name__ == "__main__":
    app.run(debug=True)
