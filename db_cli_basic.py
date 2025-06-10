import sqlite3

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
    while in_tool:
        command = input(" [BAS_CLI] > ").lower().replace(' ', '')

        if command == "exit":
            exit()
        elif command == "db_user":
            print("Type \"/help\" for help")
            connection_user: sqlite3.Connection = sqlite3.connect("database/users.db")
            cursor_user: sqlite3.Cursor = connection_user.cursor()
            while command != "/bye":
                command: str = input(" [user] > ")
                if command == "/help":
                    help_msg_db()
                elif command == "/script":
                    script = input("Type script path: ")
                    try:
                        with open(script, 'r') as script_file:
                            script = script_file.read()
                            script_file.close()

                        run_script(cursor_user, script)
                    except Exception as e:
                        print(f"Encountered error while running script:\n{e}")

                    print("Success.")
                elif command != "/bye":
                    try:
                        cursor_user.execute(command)
                    except Exception as e:
                        print(f"Failed to run command\n{e}")
        elif command == "db_data":
            print("Type \"/help\" for help")
            connection_data: sqlite3.Connection = sqlite3.connect("database/data.db")
            cursor_data: sqlite3.Cursor = connection_data.cursor()
            while command != "/bye":
                command: str = input(" [data] > ")
                if command == "/help":
                    help_msg_db()
                elif command == "/script":
                    script = input("Type script path: ")
                    try:
                        with open(script, 'r') as script_file:
                            script = script_file.read()
                            script_file.close()

                        run_script(cursor_data, script)
                    except Exception as e:
                        print(f"Encountered error while running script:\n{e}")

                    print("Success.")
                elif command != "/bye":
                        try:
                            cursor_data.execute(command)
                        except Exception as e:
                            print(f"Failed to run command\n{e}")
        elif command == "db_models":
            print("Type \"/help\" for help")
            connection_models: sqlite3.Connection = sqlite3.connect("database/models.db")
            cursor_models: sqlite3.Cursor = connection_models.cursor()
            while command != "/bye":
                command: str = input(" [models] > ")
                if command == "/help":
                    help_msg_db()
                elif command == "/script":
                    script = input("Type script path: ")
                    try:
                        with open(script, 'r') as script_file:
                            script = script_file.read()
                            script_file.close()

                        run_script(cursor_models, script)
                    except Exception as e:
                        print(f"Encountered error while running script:\n{e}")

                    print("Success.")
                elif command != "/bye":
                        try:
                            cursor_models.execute(command)
                        except Exception as e:
                            print(f"Failed to run command\n{e}")
        else:
            print(f"Unknown command \"{command}\". Use the following:\n\t\"exit\" - Exits the db CLI\n\t\"db_user\" - Enters an SQL command line for the user database\n\t\"db_data\" - Enters an SQL command line for the data database\n\t\"db_models\" - Enters an SQL command line for the models database")
else:
    print("CLI is only to be used in the Console until I change my mind.")
    exit(1)