from unittest.mock import patch, MagicMock


def mock_database_connection():
    # Patch the psycopg2.connect function to use a mock
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Mock the cursor and its methods
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [("Example", "Data")]

        # Return the mock connection for use in the app
        return mock_conn
