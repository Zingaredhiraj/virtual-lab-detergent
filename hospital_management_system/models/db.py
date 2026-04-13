"""
Database connection helper using MySQL Connector.
Uses prepared statements to prevent SQL injection.
"""
import mysql.connector
from mysql.connector import Error
from config import Config


def get_db_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def execute_query(query, params=None, fetch=False, fetchone=False, commit=False):
    """
    Execute a SQL query with prepared statements.
    
    Args:
        query: SQL query string with %s placeholders
        params: Tuple of parameters for prepared statement
        fetch: If True, return all results
        fetchone: If True, return single result
        commit: If True, commit the transaction
    
    Returns:
        Query results or last row id for INSERT operations
    """
    connection = get_db_connection()
    if not connection:
        return None

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
            return result
        elif fetchone:
            result = cursor.fetchone()
            return result
        elif commit:
            connection.commit()
            return cursor.lastrowid
    except Error as e:
        if commit:
            connection.rollback()
        print(f"Database error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def execute_transaction(queries_and_params):
    """
    Execute multiple queries in a single transaction.
    Used for billing and other operations requiring atomicity.
    
    Args:
        queries_and_params: List of (query, params) tuples
    
    Returns:
        True if transaction succeeds, False otherwise
    """
    connection = get_db_connection()
    if not connection:
        return False

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        connection.start_transaction()

        for query, params in queries_and_params:
            cursor.execute(query, params or ())

        connection.commit()
        return True
    except Error as e:
        connection.rollback()
        print(f"Transaction error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def init_database():
    """Initialize the database by running the schema SQL file."""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT
        )
        cursor = connection.cursor()

        # Read and execute schema file
        import os
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')

        # Check if schema file exists in the current directory
        if not os.path.exists(schema_path):
            schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')

        with open(schema_path, 'r') as f:
            sql_commands = f.read()

        # Execute each statement separately
        for statement in sql_commands.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except mysql.connector.Error:
                    pass  # Skip errors for existing tables/data

        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")
        return True
    except Error as e:
        print(f"Error initializing database: {e}")
        return False
