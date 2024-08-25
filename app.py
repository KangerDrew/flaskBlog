import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, request, session, jsonify
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


@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return a 204 No Content response


@app.route("/")
def home():
    # First need to check if user is logged in
    # originally had session["loggedin"], but loggedin might not be defined!
    if session.get("loggedin", False):
        return jsonify({"message": "You are currently logged in."}), 200

    # Otherwise, re-direct them to the login page:
    return jsonify({"message": "You are not that guy."}), 200


@app.route("/login", methods=["POST"])
def login():

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

            # Send back login confirmation result:
            return jsonify({"message": "Login successful!"}), 200

    # Account not found, return error
    return jsonify({"message": "Account information not found."}), 400


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.clear()
    # Redirect to login page
    return jsonify({"message": "You are now logged out."}), 200


# Checkout how "cursor" works: https://www.youtube.com/watch?v=eEikNXAsx20
@app.route("/blog", methods=["GET", "POST"])
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
                return jsonify({"message": "Your new blogs here", "content": all_blogs}), 200

            elif request.method == "POST":
                # Create a new blog post
                title = request.form["title"]
                content = request.form["content"]
                current_t = datetime.now()

                cursor.execute("INSERT INTO blog (username, title, content, created_at) VALUES (%s, %s, %s, %s)",
                               (username, title, content, current_t))
                conn.commit()
                return jsonify({"message": "New blog successfully created."}), 200

    # If user is not logged in, send back 401 code
    return jsonify({"message": "You need to login first to access your blogs."}), 401


@app.route("/edit_blog/<int:blog_id>", methods=["PUT"])
def edit_blog(blog_id):

    if not session.get("loggedin"):
        return jsonify({"message": "You need to login first to edit your blogs."}), 401

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

        # Fetch username
        username = session["username"]

        # Update an existing blog post
        new_title = request.form["title"]
        new_content = request.form["content"]

        # TODO: Implemented "edited at" feature

        cursor.execute("UPDATE blog SET content = %s, title = %s WHERE blog_id = %s AND username = %s",
                       (new_content, new_title, blog_id, username))

        # Check the number of rows affected
        if cursor.rowcount == 0:
            return jsonify({"failure": "Blog entry not found or you don't have permission to edit it."}), 404

        conn.commit()
        return jsonify({"edited_blog": blog_id})


@app.route("/delete_blog/<int:blog_id>", methods=["DELETE"])
def delete_blog(blog_id):

    if not session.get("loggedin"):
        return jsonify({"message": "You need to login first to delete your blogs."}), 401

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

        username = session["username"]
        cursor.execute("DELETE FROM blog WHERE blog_id = %s AND username = %s", (blog_id, username))

        # Check the number of rows affected
        if cursor.rowcount == 0:
            return jsonify({"failure": "Blog entry not found or you don't have permission to delete it."}), 404

        conn.commit()
        return jsonify({"deleted_blog": blog_id})


if __name__ == "__main__":
    app.run(debug=True)
