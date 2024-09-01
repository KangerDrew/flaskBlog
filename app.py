import os
from dotenv import load_dotenv
from connector import db_connect
from flask import Flask, request, session
from flask_bcrypt import Bcrypt
from datetime import datetime
from APIResponse import APIResponse

# Currently following tutorial from this:
# https://tutorial101.blogspot.com/2021/04/python-flask-postgresql-login-register.html
# https://www.youtube.com/watch?v=xIiNYn0q1gs

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")
bcrypt = Bcrypt(app)

USE_MOCK_DB = os.getenv("USE_MOCK_DB", "False") == "True"


# Singleton Code Structure Implementation:
response_formatter = APIResponse()


@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return a 204 No Content response


@app.route("/")
def home():
    # First need to check if user is logged in
    # originally had session["loggedin"], but loggedin might not be defined!
    if session.get("loggedin", False):
        return response_formatter.generate_response_s("You are currently logged in."), 200

    # Otherwise, re-direct them to the login page:
    return response_formatter.generate_response_s("You are not that guy."), 200


@app.route("/login", methods=["POST"])
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


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.clear()
    # Redirect to login page
    return response_formatter.generate_response_s("You are now logged out."), 200


@app.route('/blog', methods=["GET"])
def blog_get():

    # First need to check if user is logged in
    if not session.get("loggedin", False):
        response_formatter.generate_response_f("You need to login first to access your blogs."), 401

    # Fetch username
    username = session["username"]

    # Query database:
    query = "SELECT * FROM blog WHERE username = %s"
    params = (username,)
    all_blogs = db_connect(query, params, True)

    # TODO: Also retrieve category information pertaining to the blogs!!

    return response_formatter.generate_response_s("Your new blogs here", all_blogs), 200


@app.route('/blog', methods=["POST"])
def blog_post():

    # First need to check if user is logged in
    if not session.get("loggedin", False):
        response_formatter.generate_response_f("You need to login first to create new blogs."), 401

    # Fetch username
    username = session["username"]

    # Get a new blog content from request:
    title = request.form["title"]
    content = request.form["content"]
    current_t = datetime.now()

    # Send insert statement to database:
    query = "INSERT INTO blog (username, title, content, created_at) VALUES (%s, %s, %s, %s)"
    params = (username, title, content, current_t)
    response = db_connect(query, params, mod_query=True)

    print("*****************************************")
    print(response)
    print("*****************************************")

    # If response is null, it means the query to create new blog was not executed successfully:
    if response == 0:
        return response_formatter.generate_response_f("New blog was not created..."), 404

    return response_formatter.generate_response_s("New blog successfully created."), 200


@app.route("/blog", methods=["PUT"])
def blog_put():

    if not session.get("loggedin"):
        return response_formatter.generate_response_f("You need to login first to edit your blogs."), 401

    # Fetch username
    username = session["username"]

    # Update an existing blog post
    blog_id = request.form["blog_id"]
    new_title = request.form["title"]
    new_content = request.form["content"]

    # TODO: Implemented "edited at" feature

    # Send edit query to blog:
    query = "UPDATE blog SET content = %s, title = %s WHERE blog_id = %s AND username = %s"
    params = (new_content, new_title, blog_id, username)

    response = db_connect(query, params, mod_query=True)

    print("*****************************************")
    print(response)
    print("*****************************************")

    # If response is null, it means the query to edit blog was not executed successfully:
    if response == 0:
        return response_formatter.generate_response_f("Blog entry not found or you don't"
                                                      " have permission to edit it."), 404

    return response_formatter.generate_response_s(f"Blog ID#:{blog_id} has been successfully edited"), 200


@app.route("/blog", methods=["DELETE"])
def blog_delete():

    if not session.get("loggedin"):
        return response_formatter.generate_response_f("You need to login first to delete your blogs."), 401

    username = session["username"]
    blog_id = request.form["blog_id"]

    query = "DELETE FROM blog WHERE blog_id = %s AND username = %s"
    params = (blog_id, username)

    response = db_connect(query, params, mod_query=True)

    print("*****************************************")
    print(response)
    print("*****************************************")

    # If response is null, it means the query to delete blog was not executed successfully:
    if response == 0:
        return response_formatter.generate_response_f("Blog entry not found or you don't have"
                                                      " permission to delete it."
                                                      ), 404

    return response_formatter.generate_response_s(f"Blog ID#:{blog_id} has been successfully deleted"), 200


if __name__ == "__main__":
    app.run(debug=True)
