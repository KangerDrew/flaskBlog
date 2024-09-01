import os
from mock import mock_database_connection
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

USE_MOCK_DB = os.getenv("USE_MOCK_DB", "False") == "True"

if USE_MOCK_DB:
    # Use the mock database connection
    conn = mock_database_connection()
    print("Using mocked database connection.")
else:
    url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(url)
    print("Using real database connection.")


# Checkout how "cursor" works: https://www.youtube.com/watch?v=eEikNXAsx20
def db_connect(query, params, fetchall=False, mod_query=False):

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        # Execute SQL query
        cursor.execute(query, params)

        if mod_query:
            return cursor.rowcount

        conn.commit()

        return cursor.fetchall() if fetchall else cursor.fetchone()





