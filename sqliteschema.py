import sqlite3

def get_sqlite_schema(db_file):
    """
    Extracts the schema from a SQLite3 database file.

    Args:
        db_file (str): The path to the SQLite3 database file.

    Returns:
        str: The schema as a string, containing CREATE TABLE and CREATE INDEX statements.
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        schema = ""
        for table in tables:
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
            table_sql = cursor.fetchone()
            if table_sql:
                schema += table_sql[0] + ";\n"

            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{table}';")
            indexes = cursor.fetchall()
            for index in indexes:
                if index[0]: #check if sql exists, some indexes do not have sql.
                    schema += index[0] + ";\n"

        return schema
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def write_schema_to_file(schema, output_file):
    """
    Writes the schema to a file.

    Args:
        schema (str): The schema string.
        output_file (str): The path to the output file.
    """
    try:
        with open(output_file, "w") as f:
            f.write(schema)
        print(f"Schema written to {output_file}")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    db_file = "db.sqlite3"  # Replace with your database file
    output_file = "schema.sql"

    schema = get_sqlite_schema(db_file)

    if schema:
        write_schema_to_file(schema, output_file)