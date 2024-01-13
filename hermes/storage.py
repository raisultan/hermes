import sqlite3
import json


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


def write_pdf_paths(conn, pdf_paths: list, table_name: str = 'pdf_paths'):
    """Write list of PDF names to a table as a JSON string."""
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (data TEXT)")
    cursor.execute(f"DELETE FROM {table_name}")
    json_data = json.dumps(pdf_paths)
    cursor.execute(f"INSERT INTO {table_name} (data) VALUES (?)", (json_data,))
    conn.commit()


def read_pdf_paths(conn, table_name: str = 'pdf_paths'):
    """Read and return the list of PDF names from the table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT data FROM {table_name}")
    row = cursor.fetchone()
    return json.loads(row[0]) if row else []


def write_dir_path(conn, dir_path: str, table_name: str = 'dir_path'):
    """Write directory path to a table. Create the table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (data TEXT)")
    cursor.execute(f"DELETE FROM {table_name}")
    cursor.execute(f"INSERT INTO {table_name} (data) VALUES (?)", (dir_path,))
    conn.commit()


def read_dir_path(conn, table_name: str = 'dir_path'):
    """Read and return the row from the table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT data FROM {table_name}")
    row = cursor.fetchone()
    return row[0] if row else None


def disconnect_from_db(conn):
    """Disconnect from the database."""
    conn.close()
