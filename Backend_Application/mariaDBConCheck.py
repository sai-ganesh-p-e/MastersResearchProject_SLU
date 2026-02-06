import mysql.connector as mariadb  # Import the MariaDB connector

# Database connection parameters
host = "localhost"  # Database host (change if connecting to a remote server)
user = "root"       # Database username (replace with your actual username)
password = "team6@MRP"  # Database password (replace with your actual password)
database = "allyUserData"  # The database you're connecting to (replace with your actual database name)

try:
    # Establish connection to MariaDB
    conn = mariadb.connect(
        host=host,        # Host of the database
        user=user,        # Username for authentication
        password=password,  # Password for authentication
        database=database  # Name of the database to connect to
    )

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Confirm successful connection
    print("Connected to MariaDB successfully!")

except mariadb.Error as e:
    # Catch and print any errors that occur during the connection attempt
    print(f"Error connecting to MariaDB: {e}")

finally:
    # Ensure the connection is closed even if an error occurs
    if 'conn' in locals():
        conn.close()  # Close the connection to the database
        # print("Connection closed.")  # Uncomment if you want to print the closing message
