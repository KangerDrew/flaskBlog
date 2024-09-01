import os
from dotenv import load_dotenv
from connector import db_connect
from flask import Flask, request, session
from routes.auth import auth_bp
from routes.blog import blog_bp

# Currently following tutorial from this:
# https://tutorial101.blogspot.com/2021/04/python-flask-postgresql-login-register.html
# https://www.youtube.com/watch?v=xIiNYn0q1gs

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(blog_bp)


@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return a 204 No Content response


if __name__ == "__main__":
    app.run(debug=True)
