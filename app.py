"""
AUTHOR: LUEWASHERE
DOB: 6/9/2025
LAST MOD: 6/10/2025

VERSION: 0.3
"""
# Web imports
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for

# Database imports
import sqlite3

# Other imports
import os
import logging
import database.lib.database_manager as db_lib

# +===================================+
# |                                   |
# |      app.py, the backend if       |
# |             you will              |
# |                                   |
# +===================================+

# Setup logging
# Create a logger
logger: logging.Logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)  # Set the logging level

# Create a file handler to log to a file
file_handler: logging.FileHandler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)  # Log all levels to the file

# Create a console handler to log to the console
console_handler = logging.StreamHandler() # Don't type specify for this
console_handler.setLevel(logging.INFO)  # Log only INFO and above to the console

# Create a formatter and set it for both handlers
formatter: logging.Formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Logger setup!")

# Flask setup
app = Flask(__name__)

@app.route("/")
def default_page():
    return redirect(url_for("chat"))

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/auth")
def auth():
    return render_template("auth.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

# Database functions
def load_db_script(script_name: str) -> str:
    with open(f"database/scripts/{script_name}.sql") as script_file:
        script: str = script_file.read()

    return script

def database_check_success(operation: str, database: str, succ: dict[str, str]) -> None:
    if succ["success"] != "fail":
        logger.info(f"\"{operation}\" on {database} was a Success.")
    else:
        logger.critical(f"Failed to {operation} on {database}!")
        logger.info(f"Failure output: {succ["reason"]}")
        exit(1)
    
    return

def create_databases() -> dict[str, str]:
    try:
        # Create files
        connection_user: sqlite3.Connection = sqlite3.connect(os.path.join("database", "users.db"))
        connection_data: sqlite3.Connection = sqlite3.connect(os.path.join("database", "data.db"))
        connection_model: sqlite3.Connection = sqlite3.connect(os.path.join("database", "models.db"))
    
        # Create cursors
        cursor_user: sqlite3.Cursor = connection_user.cursor()
        cursor_data: sqlite3.Cursor = connection_data.cursor()
        cursor_model: sqlite3.Cursor = connection_model.cursor()

        # Load scripts
        data_script: str = load_db_script("create_data_db")
        user_script: str = load_db_script("create_user_db")
        model_script: str = load_db_script("create_models_db")

        # Execute script
        cursor_user.executescript(user_script)
        cursor_data.executescript(data_script)
        cursor_model.executescript(model_script)
    except Exception as e:
        return {"success": "fail", "reason": str(e).replace('\n', '     \\n     ')}

    return {"success": "success"}

def database_fix_missing() -> dict[str, str]:
    try:
        check_for: list[str] = ["data.db", "users.db", "models.db"]

        for db in check_for:
            if db not in os.listdir("database"):
                connection_db: sqlite3.Connection = sqlite3.connect(f"database/{db}") # Create database
                cursor_db: sqlite3.Cursor = connection_db.cursor() # Create cursor
                db_script: str = load_db_script(f"create_{db.replace('.db', '')}_db") # Load script
                cursor_db.executescript(db_script) # Execute script

                logger.info(f"Fixed {db}")
    except Exception as e:
        return {"success": "fail", "reason": str(e).replace('\n', '     \\n     ')}

    return {"success": "success"}

def delete_databases() -> dict[str, str]:
    raise NotImplementedError
    return {"success": "fail", "reason": "Unknown"}

def delete_database(database: str="users") -> dict[str, str]:
    raise NotImplementedError
    return {"success": "fail", "reason": "Unknown"}

# Add other functions for specific queries later...

def main() -> None:
    # Check databases exist variables
    usersDbExists: bool = "users.db" in os.listdir("database")
    dataDbExists: bool = "data.db" in os.listdir("database")
    modelsDbExists: bool = "models.db" in os.listdir("database")

    # Check for missing databases, create new ones if needed
    if not usersDbExists and not dataDbExists and not modelsDbExists:
        logger.info("Creating databases...")
        succ: dict[str, str] = create_databases()
        database_check_success("create", "both databases", succ)
    elif [usersDbExists, dataDbExists, modelsDbExists] != [True, True, True]:
        logger.warning("The following databases are missing: ")
        for db, exists in {"User database": usersDbExists, "Data database": dataDbExists, "Models database": modelsDbExists}.items():
            logger.warning(db if not exists else ("-" * len(db)))

        succ: dict[str, str] = database_fix_missing()
        database_check_success("fix missing", "missing databases", succ)

    logger.info("All databases exist.")

    # Create class instances
    data_db = db_lib.Data_DB()
    users_db = db_lib.Users_DB()
    models_db = db_lib.Models_DB()

    app.run()
    

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An unexpected error has occoured:\n{e}")