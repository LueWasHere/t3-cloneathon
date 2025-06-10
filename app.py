"""
AUTHOR: LUEWASHERE
DOB: 6/9/2025
LAST MOD: 6/9/2025

VERSION: 0.1
"""
# Web imports
import flask

# Database imports
import sqlite3

# Other imports
import os
import logging

# +===================================+
# |                                   |
# |      app.py, the backend if       |
# |             you will              |
# |                                   |
# +===================================+

# Setup logging
# Create a logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)  # Set the logging level

# Create a file handler to log to a file
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)  # Log all levels to the file

# Create a console handler to log to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Log only INFO and above to the console

# Create a formatter and set it for both handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Logger setup!")

# Database functions
def load_db_script(script_name: str) -> str:
    with open(f"database/scripts/{script_name}.sql") as script_file:
        script = script_file.read()
        script_file.close()

    return script

def database_check_success(operation: str, database: str, succ: dict) -> None:
    if succ["success"] != "fail":
        logger.info(f"\"{operation}\" on {database} was a Success.")
    else:
        logger.critical(f"Failed to {operation} on {database}!")
        logger.info(f"Failure output: {succ["reason"]}")
        exit(1)
    
    return

def create_databases() -> dict:
    try:
        # Create files
        connection_user = sqlite3.connect("database/users.db")
        connection_data = sqlite3.connect("database/data.db")
    
        # Create cursors
        cursor_user = connection_user.cursor()
        cursor_data = connection_data.cursor()

        # Load scripts
        data_script = load_db_script("create_data_db")
        user_script = load_db_script("create_user_db")

        # Add necessary columns
        cursor_user.executescript(user_script)
        cursor_data.executescript(data_script)

        return {"success": "success"}
    except Exception as e:
        return {"success": "fail", "reason": str(e).replace('\n', '     \\n     ')}

    return {"success": "fail", "reason": "Unknown"}

def database_fix_missing() -> dict:
    return {"success": "fail", "reason": "Unknown"}

def delete_databases() -> dict:
    return {"success": "fail", "reason": "Unknown"}

def delete_database(database: str="users") -> dict:
    return {"success": "fail", "reason": "Unknown"}

# Add other functions for specific queries later...

# Init database
usersDbExists = "users.db" in os.listdir("database")
dataDbExists = "data.db" in os.listdir("database")

# Check for missing databases, create new ones if needed
if not usersDbExists and not dataDbExists:
    logger.info("Creating databases...")
    succ = create_databases()
    database_check_success("create", "both databases", succ)
elif (usersDbExists and not dataDbExists) or (dataDbExists and not usersDbExists):
    logger.warning(f"{"Users" if not dataDbExists else "Data"} database exists but not {"Users" if dataDbExists else "Data"}? Consider resetting the databases!")
    logger.info(f"Creating {"Users" if dataDbExists else "Data"}.db...")
    succ = database_fix_missing()
    database_check_success("create", "Users" if dataDbExists else "Data", succ)
