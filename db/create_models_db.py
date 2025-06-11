import sqlite3
import os

# --- Configuration ---
SQL_FILE = 'create_models_db.sql'
DATABASE_FILE = 'models.db'

def create_database():
    """
    Reads a structured SQL file and executes it to create and populate 
    a SQLite database with multiple tables.
    Deletes the old database file if it exists to ensure a fresh build.
    """
    # 1. Check if the SQL file exists
    if not os.path.exists(SQL_FILE):
        print(f"Error: The SQL file '{SQL_FILE}' was not found.")
        print("Please make sure it's in the same directory as this script.")
        return

    # 2. Remove the old database file if it exists
    if os.path.exists(DATABASE_FILE):
        print(f"Removing existing database file: '{DATABASE_FILE}'")
        os.remove(DATABASE_FILE)

    # 3. Read the entire SQL script
    try:
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        print(f"Successfully read SQL script from '{SQL_FILE}'.")
    except Exception as e:
        print(f"Error reading SQL file: {e}")
        return

    # 4. Connect to the SQLite database and execute the script
    conn = None
    try:
        print(f"Creating and connecting to database: '{DATABASE_FILE}'...")
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        print("Executing SQL script to create tables and insert data...")
        # executescript can handle a file with multiple SQL statements
        cursor.executescript(sql_script)

        # 5. Commit the changes
        conn.commit()
        print("Data inserted successfully into all tables.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback() # Rollback changes on error
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    create_database()
    print(f"\nProcess complete. Your database '{DATABASE_FILE}' with the new 'api_name' column should be ready.")