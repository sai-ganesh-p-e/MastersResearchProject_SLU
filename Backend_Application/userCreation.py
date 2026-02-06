import mysql.connector as mariadb
from getpass import getpass
import bcrypt
import re
from datetime import datetime

# Connect to the MariaDB database
db_connection = mariadb.connect(
    host="localhost",
    user="root",
    password="team6@MRP",
    database="allyUserData"
)

cursor = db_connection.cursor()

# Function to check if a field (username, bank account number, mobile number) already exists in the database
def is_field_unique(field_name, value):
    query = f"SELECT * FROM Customers WHERE {field_name} = %s"
    cursor.execute(query, (value,))
    return cursor.fetchone() is None

# Function to securely hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Function to validate the format of the bank account number (8-17 digits)
def validate_bank_account_number(account_number):
    return bool(re.match(r'^\d{8,17}$', account_number))

# Function to validate mobile number (exactly 10 digits)
def validate_mobile_number(mobile_number):
    return bool(re.match(r'^\d{10}$', mobile_number))

# Function to validate date of birth in the format YYYY-MM-DD
def validate_dob(date_of_birth):
    try:
        datetime.strptime(date_of_birth, "%Y-%m-%d")  # Ensures correct format
        return True
    except ValueError:
        return False

# Function to validate password strength (minimum 8 characters, including uppercase, lowercase, special characters)
def validate_password_strength(password):
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password))

# Function to get user input for registration
def get_user_input():
    while True:
        # Get a unique username from the user
        username = input("Enter a unique username: ").strip()
        if username and is_field_unique("username", username):
            break
        print("❌ Username already exists or is empty. Try again.")

    while True:
        # Get password from the user and validate strength
        password = getpass("Enter password (min 8 chars, 1 uppercase, 1 special char): ").strip()
        if validate_password_strength(password):
            # Confirm password to ensure they match
            confirm_password = getpass("Confirm password: ").strip()
            if password == confirm_password:
                hashed_password = hash_password(password)
                break
            else:
                print("❌ Passwords do not match. Try again.")
        else:
            print("❌ Password must be at least 8 characters long and include an uppercase letter, lowercase letter, a digit, and a special character.")

    while True:
        # Get first name from the user
        firstname = input("Enter first name: ").strip()
        if firstname:
            break
        print("❌ First name cannot be empty.")

    while True:
        # Get last name from the user
        lastname = input("Enter last name: ").strip()
        if lastname:
            break
        print("❌ Last name cannot be empty.")

    while True:
        # Get date of birth and validate format
        dob = input("Enter date of birth (YYYY-MM-DD): ").strip()
        if validate_dob(dob):
            break
        print("❌ Invalid date of birth format. Use YYYY-MM-DD.")

    while True:
        # Get bank account number and validate
        bank_account_number = input("Enter bank account number (8-17 digits): ").strip()
        if validate_bank_account_number(bank_account_number) and is_field_unique("bank_account_number", bank_account_number):
            break
        print("❌ Invalid or duplicate bank account number. Must be 8-17 digits.")

    while True:
        # Get account balance and ensure it's a valid number
        account_balance = input("Enter account balance: ").strip()
        if account_balance.replace('.', '', 1).isdigit():
            break
        print("❌ Invalid account balance. Must be a number.")

    while True:
        # Get account type (checking/savings)
        account_type = input("Enter account type (checking/savings): ").strip().lower()
        if account_type in ['checking', 'savings']:
            break
        print("❌ Invalid account type. Choose 'checking' or 'savings'.")

    while True:
        # Get address from the user
        address = input("Enter address: ").strip()
        if address:
            break
        print("❌ Address cannot be empty.")

    while True:
        # Get mobile number and validate
        mobile_number = input("Enter mobile number (10 digits): ").strip()
        if validate_mobile_number(mobile_number) and is_field_unique("mobile_number", mobile_number):
            break
        print("❌ Invalid or duplicate mobile number. Must be 10 digits.")

    while True:
        # Get email address from the user
        email = input("Enter email address: ").strip()
        if email:
            break
        print("❌ Email cannot be empty.")

    return (username, hashed_password, firstname, lastname, dob, bank_account_number, account_balance, account_type, address, mobile_number, email)

# Function to insert user data into the database
def insert_into_database(data):
    sql = """INSERT INTO Customers
        (username, password, firstname, lastname, dob, bank_account_number, account_balance, account_type, address, mobile_number, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, data)
    db_connection.commit()
    print("✅ User registered successfully!")

# Main function to run the registration process
def main():
    print("\n🏦 Welcome to the Bank System - User Registration 🏦\n")
    user_data = get_user_input()  # Gather all user input
    insert_into_database(user_data)  # Insert the user data into the database

# Run the script
if __name__ == "__main__":
    main()

# Close the cursor and connection when done
cursor.close()
db_connection.close()
