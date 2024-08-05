import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__)
# url = os.getenv("DATABASE_URL")
# connection = psycopg2.connect(url)

CREATE_BLOG = (
    "INSERT INTO blogs"
)


@app.get("/")
def home():
    return "<h1>My VERY COOL Blog :D</h1>"


@app.route("/login")
def login():
    return "Login Here"


if __name__ == "__main__":
    app.run(debug=True)
