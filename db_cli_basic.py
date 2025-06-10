"""
AUTHOR: LUEWASHERE
DOB: 6/9/2025
LAST MOD: 6/10/2025

VERSION: 1.0
"""

import sqlite3
import os

# +===================================+
# |                                   |
# |      db_cli_basic.py, a baic      |
# |        cli for interacting        |
# |         with the database         |
# |                                   |
# +===================================+

def run_script(cursor: sqlite3.Cursor, script: str) -> None:
    cursor.executescript(script)
    
    return

if __name__ == "__main__":
    def help_msg_db() -> None:
        print("Commands: ")
        print("\t/bye - Exit back to CLI")
        print("\t/script - Run a script")
        print("\t/help - Print this help message")

        return
    
    in_tool = True
    try:
        while in_tool:
            command = input(" [BAS_CLI] > ").lower().replace(' ', '')

            if command == "exit":
                exit()
            elif command.startswith('db_'):
                print("Type \"/help\" for help")
                database_name_build: list[str] = command.split('_')
                database_name_build.remove('db')
                if len(database_name_build) == 0:
                    print("No database name specified")
                else:
                    database_name: str = "_".join(database_name_build)
                    if f"{database_name}.db" not in os.listdir("database"):
                        yn = None
                        while (yn != 'y') and (yn != 'n'):
                            yn = input(f"{database_name}.sql doesn't exist, create it? (Y/n) ").lower()
                            if yn == 'n':
                                command = '/bye'
                    if command != "/bye":
                        connection_db: sqlite3.Connection = sqlite3.connect(f"database/{database_name}.db")
                        cursor_db: sqlite3.Cursor = connection_db.cursor()
                    while command != "/bye":
                        command: str = input(f" [{database_name}] > ")
                        if command == "/help":
                            help_msg_db()
                        elif command == "/script":
                            script = input("Type script path: ")
                            try:
                                with open(script, 'r') as script_file:
                                    script = script_file.read()

                                run_script(cursor_db, script)
                            except Exception as e:
                                print(f"Encountered error while running script:\n{e}")

                            print("Success.")
                        elif command != "/bye":
                            try:
                                cursor_db.execute(command)
                            except Exception as e:
                                print(f"Failed to run command\n{e}")
            else:
                help_msg_cli = """Use the following:
                \t\"exit\" - Exits the db CLI
                \t\"db_[DATABASE_NAME]\" - Enters an SQL command line for a specified database
                """
                print(f"Unknown command \"{command}\". {help_msg_cli}")
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected, exiting gracefully...")
else:
    print("CLI is only to be used in the Console until I change my mind.")
    exit(1)