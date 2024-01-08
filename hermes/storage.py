import sqlite3


def connect_to_db(db_file: str = 'storage.sqlite'):
    """Connect to the SQLite database specified by db_file."""
    conn = sqlite3.connect(db_file)
    return conn

def write_collection_name(conn, data, table_name: str = 'collection'):
    """Write data to a table. Create the table if it doesn't exist.
    The table will always contain only one row."""
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (data TEXT)")
    cursor.execute(f"DELETE FROM {table_name}")
    cursor.execute(f"INSERT INTO {table_name} (data) VALUES (?)", (data,))
    conn.commit()

def read_collection_name(conn, table_name: str = 'collection'):
    """Read and return the row from the table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT data FROM {table_name}")
    row = cursor.fetchone()
    return row[0] if row else None

def disconnect_from_db(conn):
    """Disconnect from the database."""
    conn.close()
