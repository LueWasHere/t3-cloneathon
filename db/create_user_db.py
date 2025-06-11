import sqlite3
import os

# --- Configuration ---
# The directory where databases are stored
DB_DIR = 'db'

# The name of the database file to create
DATABASE_NAME = 'user.db'

# The name of the SQL script to execute
SQL_SCRIPT_NAME = 'create_user_db.sql'

# --- Main Script Logic ---
def setup_user_database():
    """
    Sets up the user database by creating the necessary directory and
    executing the SQL script.
    """
    # Check if the required SQL script exists first
    if not os.path.exists(SQL_SCRIPT_NAME):
        print(f"FATAL ERROR: SQL script '{SQL_SCRIPT_NAME}' not found.")
        print("Please make sure the script is in the same directory as this Python file.")
        return # Exit the function

    # 1. Ensure the database directory exists
    print(f"Ensuring database directory '{DB_DIR}' exists...")
    os.makedirs(DB_DIR, exist_ok=True)
    print(f"Directory '{DB_DIR}' is ready.")

    # Construct the full path to the database
    db_path = os.path.join(DB_DIR, DATABASE_NAME)
    
    conn = None # Initialize connection to None
    try:
        # 2. Read the SQL commands from the file
        print(f"Reading SQL commands from '{SQL_SCRIPT_NAME}'...")
        with open(SQL_SCRIPT_NAME, 'r') as sql_file:
            sql_script = sql_file.read()
        print("SQL script loaded.")
        
        # 3. Connect to the SQLite database (this will create it if it doesn't exist)
        print(f"Connecting to database at '{db_path}'...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Connection successful.")
        
        # 4. Execute the entire SQL script
        # executescript() is used because the file may contain multiple SQL statements.
        print("Executing SQL script to create tables...")
        cursor.executescript(sql_script)
        
        # 5. Commit the changes and close the connection
        conn.commit()
        print("\nSUCCESS: Database tables created and changes committed.")
        
    except sqlite3.Error as e:
        print(f"\nDATABASE ERROR: An error occurred - {e}")
        
    finally:
        # 6. Ensure the connection is closed even if an error occurred
        if conn:
            conn.close()
            print("Database connection closed.")

# This allows the script to be run from the command line
if __name__ == '__main__':
    setup_user_database()