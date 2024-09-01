from flask import Blueprint, request, session
from datetime import datetime
from connector import db_connect
from APIResponse import APIResponse


blog_bp = Blueprint('blog', __name__)

blog_response_formatter = APIResponse()


@blog_bp.route('/blog', methods=["GET"])
def blog_get():

    # First need to check if user is logged in
    if not session.get("loggedin", False):
        blog_response_formatter.generate_response_f("You need to login first to access your blogs."), 401

    # Fetch username
    username = session["username"]

    # Query database:
    query = "SELECT * FROM blog WHERE username = %s"
    params = (username,)
    all_blogs = db_connect(query, params, True)

    # TODO: Also retrieve category information pertaining to the blogs!!

    return blog_response_formatter.generate_response_s("Your new blogs here", all_blogs), 200


@blog_bp.route('/blog', methods=["POST"])
def blog_post():

    # First need to check if user is logged in
    if not session.get("loggedin", False):
        blog_response_formatter.generate_response_f("You need to login first to create new blogs."), 401

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
        return blog_response_formatter.generate_response_f("New blog was not created..."), 404

    return blog_response_formatter.generate_response_s("New blog successfully created."), 200


@blog_bp.route("/blog", methods=["PUT"])
def blog_put():

    if not session.get("loggedin"):
        return blog_response_formatter.generate_response_f("You need to login first to edit your blogs."), 401

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
        return blog_response_formatter.generate_response_f("Blog entry not found or you don't"
                                                           " have permission to edit it."), 404

    return blog_response_formatter.generate_response_s(f"Blog ID#:{blog_id} has been successfully edited"), 200


@blog_bp.route("/blog", methods=["DELETE"])
def blog_delete():

    if not session.get("loggedin"):
        return blog_response_formatter.generate_response_f("You need to login first to delete your blogs."), 401

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
        return blog_response_formatter.generate_response_f("Blog entry not found or you don't have"
                                                           " permission to delete it."
                                                           ), 404

    return blog_response_formatter.generate_response_s(f"Blog ID#:{blog_id} has been successfully deleted"), 200
