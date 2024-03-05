import sqlite3

def print_database(db_file):
    # Connect to the database
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    # Get a list of tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    # Iterate over the tables
    for table in tables:
        table_name = table[0]
        print(f'Table: {table_name}')
        # Get a list of columns in the table
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        # Print the column names
        print(' | '.join(column_names))
        # Query the database for all rows in the table
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()
        # Iterate over the rows
        for row in rows:
            # Print the row data
            print(' | '.join(map(str, row)))
    # Close the connection
    connection.close()
