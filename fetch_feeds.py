import mysql.connector
from mysql.connector import Error

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Rihan@6226',
        database='intern'
    )


def fetch_feeds_from_db():
    data = []
    columns = []
    error_db = None    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM feed_entries")  # Adjust this if necessary
        data = cursor.fetchall()
        columns = [i[0] for i in cursor.description]  # Get column names
    except Error as e:
        print(f"Error: {e}")
        error_db = e
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return data,columns,error_db