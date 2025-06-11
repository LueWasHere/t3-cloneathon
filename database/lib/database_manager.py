import sqlite3
import os
import logging

# Database functions
def load_db_script(script_name: str) -> str:
    with open(f"database/scripts/{script_name}.sql") as script_file:
        script: str = script_file.read()

    return script

def database_check_success(operation: str, database: str, succ: dict[str, str], logger: logging.Logger) -> None:
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

def database_fix_missing(logger: logging.Logger) -> dict[str, str]:
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

class Data_DB:
    def __init__(self) -> None:
        pass

class Users_DB:
    def __init__(self) -> None:
        pass

class Models_DB:
    def __init__(self) -> None:
        self.DB_DIR = 'database'
        self.DB_PATH = os.path.join(self.DB_DIR, 'models.db')
        
        self.conns: dict[int, sqlite3.Connection] = {}

    def get_db_conn(self) -> sqlite3.Connection:
        conn: sqlite3.Connection = sqlite3.connect(self.DB_PATH)
        conn.row_factory = sqlite3.Row

        id = len(self.conns.keys())
        self.conns[id] = conn
        return id, conn
    
    def destroy_conn(self, id) -> None:
        self.conns[id].close()
        self.conns[id] = None

        return