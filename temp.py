import sqlite3
import os

# --- Configuration ---
# The hard-coded path to your database file.
# The r"..." syntax (raw string) is important for Windows paths to prevent issues with backslashes.
DATABASE_FILE_PATH = r"C:\Users\green\t3_clone\db\models.db"

def print_database_contents(db_path: str):
    """
    Connects to a SQLite database, lists all tables, and prints the full
    contents of each table.
    """
    # 1. Check if the database file actually exists
    if not os.path.exists(db_path):
        print(f"🔴 ERROR: Database file not found at the specified path.")
        print(f"   -> Searched for: {db_path}")
        return

    print(f"📖 Reading database from: {db_path}")

    try:
        # 2. Connect to the database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # 3. Get a list of all tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cursor.fetchall()
            
            if not tables:
                print("\nDatabase is empty or contains no tables.")
                return

            table_names = [table[0] for table in tables]
            print(f"Found tables: {', '.join(table_names)}")

            # 4. Loop through each table and print its contents
            for table_name in table_names:
                print("\n\n" + "="*80)
                print(f"====== Contents of table: {table_name} ")
                print("="*80)

                # Fetch all rows from the current table
                cursor.execute(f"SELECT * FROM {table_name}")
                
                # Get column headers
                col_names = [description[0] for description in cursor.description]
                rows = cursor.fetchall()

                if not rows:
                    print("... table is empty ...")
                    continue

                # Print headers
                header_string = " | ".join(col_names)
                print(header_string)
                print("-" * len(header_string))

                # Print each row
                for row in rows:
                    # Convert all items in the row to a string, handling None values
                    row_str = [str(item) if item is not None else "NULL" for item in row]
                    print(" | ".join(row_str))

    except sqlite3.Error as e:
        print(f"🔴 DATABASE ERROR: An error occurred while reading the database: {e}")
    except Exception as e:
        print(f"🔴 UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    print_database_contents(DATABASE_FILE_PATH)
    print("\n\n--- End of database dump ---")