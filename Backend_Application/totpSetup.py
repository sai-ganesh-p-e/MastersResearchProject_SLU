import mysql.connector as mariadb
from getpass import getpass
import bcrypt
import pyotp
import time
import os

# Restart the NTP service to ensure accurate time synchronization
os.system("sudo systemctl restart chronyd")

import qrcode
import pytz
from datetime import datetime

# File paths for logging user events
LOG_FILE_PATH = "/home/mshrinivasan/login_log.txt"
TESTRUN_LOG_PATH = "/home/mshrinivasan/testrun-log.txt"

# Establish a connection to the MariaDB database
db_connection = mariadb.connect(
    host="localhost",
    user="root",
    password="team6@MRP",  # Please ensure the password is stored securely in production
    database="allyUserData"  # Database containing customer information
)
cursor = db_connection.cursor()

# Function to log events with timestamps, which helps with debugging and audit trails
def log_event(event, test_run=False):
    log_file = TESTRUN_LOG_PATH if test_run else LOG_FILE_PATH
    with open(log_file, "a") as file:
        file.write(f"{datetime.now()} - {event}\n")

# Fetch the stored password hash from the database for a given username
def get_stored_password(username):
    query = "SELECT password FROM Customers WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    return result[0] if result else None

# Fetch the stored TOTP secret for the user, used for two-factor authentication (2FA)
def get_totp_secret(username):
    query = "SELECT totp_secret FROM Customers WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    return result[0] if result else None

# Fetch the backup code for the user, used if TOTP verification fails
def get_backup_code(username):
    query = "SELECT backup_code FROM Customers WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    return result[0] if result else None

# Verify entered password against the stored hashed password using bcrypt
def verify_password(entered_password, stored_hashed_password):
    return bcrypt.checkpw(entered_password.encode(), stored_hashed_password.encode())

# Generate a random TOTP secret key
def generate_totp_secret():
    return pyotp.random_base32()

# Generate a random backup code
def generate_backup_code():
    return os.urandom(8).hex()

# Display the QR code for TOTP setup, making it user-friendly
def display_qr_code(qr_code_url):
    qr = qrcode.QRCode()
    qr.add_data(qr_code_url)
    qr.make(fit=True)
    qr.print_ascii()


# Function to provide a downloadable link of the TOTP guide
def provide_totp_guide():
    # You can update this with either a local path or a URL to the TOTP guide
    # For example, the PDF file can be served from a server or stored locally
    guide_link = "/root/MastersResearchProject_SLU/Frontend_Application/static/TOTPSetupGuide.pdf"  # Modify this with your actual path or URL
    print(f"\n📥 Download the TOTP Guide PDF: {guide_link}")
    print("You can download the TOTP guide from the link above to help you set up your authenticator app.")

# Set up TOTP for a user, including generating the secret, QR code, and backup code
def setup_totp(username):
    secret = generate_totp_secret()  # Generate a TOTP secret key
    totp = pyotp.TOTP(secret)  # Create the TOTP object
    timezone = pytz.timezone("America/Chicago")  # Assuming the user is in Central Time Zone
    qr_code_url = totp.provisioning_uri(username, issuer_name="Ally Bank")  # QR code for the authenticator app

    print("\n📲 Scan this QR code with your authenticator app:")
    display_qr_code(qr_code_url)  # Show the QR code

    # Provide downloadable link to the TOTP guide
    provide_totp_guide()

    backup_code = generate_backup_code()
    print(f"\n🔑 Your backup code: {backup_code} (Store this in a **secure place**!)")
    print("\nIf you cannot scan the QR code, please use the following secret key to manually set up TOTP in your app:")
    print(f"Secret key: {secret}")

    # Prompt user to confirm TOTP setup by entering the backup code
    user_input = input("Please confirm your TOTP setup by entering your backup code: ").strip()

    # Validate user input against the generated backup code
    if user_input == backup_code:
        print("✅ TOTP setup confirmed successfully!")
    else:
        print("❌ Incorrect backup code. Please try setting up TOTP again.")
        return False

    # Ask user to enter the auth code from their app
    attempts = 3
    while attempts > 0:
        entered_code = input("Enter the authentication code from your authenticator app: ").strip()
        if totp.verify(entered_code):  # Validate the entered TOTP code
            print("✅ TOTP setup complete! Access granted.")
            update_query = "UPDATE Customers SET totp_secret = %s, backup_code = %s WHERE username = %s"
            cursor.execute(update_query, (secret, backup_code, username))
            db_connection.commit()  # Save the changes to the database
            return True
        else:
            print(f"❌ Incorrect authentication code. Attempts left: {attempts-1}")
            attempts -= 1

    # If TOTP fails after 3 attempts, ask for the backup code
    print("❌ Too many incorrect TOTP attempts. Please use your backup code.")
    if prompt_for_backup_code(username):  # Validate backup code
        print("✅ Backup code verified! Access granted.")
        return True
    else:
        print("❌ Invalid backup code. Exiting...")
        return False

# Verify the TOTP code entered by the user
def verify_totp(secret):
    totp = pyotp.TOTP(secret)
    local_time = datetime.now(pytz.timezone("America/Chicago"))  # Show local time for transparency
    print(f"🕒 Your local time: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")

    entered_code = input("Enter the TOTP code from your authenticator app: ").strip()
    return totp.verify(entered_code)  # Validate the code entered by the user

# Prompt the user for their password, allowing up to 3 attempts
def prompt_for_password():
    attempts = 3
    while attempts > 0:
        entered_password = getpass("Enter your password: ").strip()
        if entered_password:
            return entered_password
        print(f"⚠ Incorrect or empty password. Attempts left: {attempts-1}")
        attempts -= 1

    print("❌ Too many incorrect password attempts. Exiting...")
    log_event("User exceeded password attempts.")
    exit()

# Prompt the user for their backup code, allowing up to 3 attempts
def prompt_for_backup_code(username):
    backup_code = get_backup_code(username)
    attempts = 3
    while attempts > 0:
        entered_backup = input("Enter your backup code: ").strip()
        if entered_backup == backup_code:
            print("✅ Backup code verified! Access granted.")
            return True
        else:
            print(f"❌ Incorrect backup code. Attempts left: {attempts-1}")
            log_event(f"User {username} entered incorrect backup code. Attempts left: {attempts-1}")

        attempts -= 1

    print("❌ Too many incorrect backup code attempts. Exiting...")
    log_event(f"User {username} exceeded backup code attempts.")
    exit()

# Main login function, handles user login with password and TOTP/backup code
def login():
    attempts = 3
    while attempts > 0:
        username = input("Enter your username: ").strip()
        stored_hashed_password = get_stored_password(username)

        if not stored_hashed_password:
            print("❌ Username not found. Please tTry again.")
            continue

        entered_password = prompt_for_password()

        # Verify entered password against stored hash
        if verify_password(entered_password, stored_hashed_password):
            print("✅ Login successful!")
            log_event(f"User {username} logged in successfully.")

            secret = get_totp_secret(username)  # Fetch the TOTP secret for the user

            if not secret:
                print("\n🔒 We are migrating to TOTP-based authentication by May 17th, 2025.")
                choice = input("Would you like to set up TOTP now? (yes/no): ").strip().lower()
                if choice == "yes":
                    if setup_totp(username):  # Set up TOTP for the user
                        print("✅ TOTP setup complete. Use your authenticator app for future logins.")
                        log_event(f"User {username} set up TOTP.")
                else:
                    print("⚠ You must set up TOTP by May 17th, 2025 for secure banking.")

            # Verify TOTP or allow backup code usage if TOTP fails
            if secret:
                print("\n🔑 TOTP Verification")
                if verify_totp(secret):  # Verify the TOTP code
                    print("✅ TOTP Verified! Access granted.")
                else:
                    print("⚠ TOTP failed. Do you want to use your backup code? (yes/no)")
                    use_backup = input().strip().lower()
                    if use_backup == "yes":
                        if prompt_for_backup_code(username):
                            pass  # Backup code verified, proceed
                    else:
                        print("❌ TOTP verification failed. Exiting...")
                        return

            # Display customer info after successful login
            customer_info = get_customer_info(username)
            if customer_info:
                print("\n🏦 Customer Information 🏦")
                print(f"Customer Name: {customer_info[1]}")
                print(f"Account Number: {customer_info[7]}")
                print(f"Account Balance: ${customer_info[8]}")
                print(f"Account Type: {customer_info[12]}")
                print(f"Address: {customer_info[10]}")
                print(f"Mobile Number: {customer_info[11]}")
                print(f"Email: {customer_info[9]}")
                log_event(f"Displayed customer info for {username}.")

            # Handle user logout options
            while True:
                logout_choice = input("Do you want to logout? (yes/no): ").strip().lower()
                if logout_choice == "yes":
                    print("🔒 Logged out successfully!")
                    log_event(f"User {username} logged out.")
                    return
                elif logout_choice == "no":
                    print("You are still logged in.")
                    setup_choice = input("Do you want to set up TOTP again? (yes/no): ").strip().lower()
                    if setup_choice == "yes":
                        if setup_totp(username):
                            print("✅ TOTP setup complete. Access granted.")
                            log_event(f"User {username} set up TOTP again.")
                            # Show customer info after second TOTP setup
                            customer_info = get_customer_info(username)
                            if customer_info:
                                print("\n🏦 Customer Information 🏦")
                                print(f"Customer Name: {customer_info[1]}")
                                print(f"Account Number: {customer_info[7]}")
                                print(f"Account Balance: ${customer_info[8]}")
                                print(f"Account Type: {customer_info[12]}")
                                print(f"Address: {customer_info[10]}")
                                print(f"Mobile Number: {customer_info[11]}")
                                print(f"Email: {customer_info[9]}")
                                log_event(f"Displayed customer info for {username}.")
                        else:
                            print("❌ Exiting setup process.")
                    else:
                        print("Exiting...")
                        return
                else:
                    print("Invalid choice. Enter 'yes' or 'no'.")
        else:
            print("❌ Incorrect password. Try again.")
            log_event(f"Failed login attempt for {username}.")
            attempts -= 1

    print("❌ Too many failed login attempts. Exiting...")
    log_event("User exceeded login attempts.")

# Fetch customer details from the database
def get_customer_info(username):
    query = "SELECT * FROM Customers WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone()

# Main function to initiate the process
def main():
    log_event("Backend execution started.", test_run=True)
    print("\n🏦 Welcome to the Ally Bank - User Login 🏦\n")
    login()
    log_event("Backend execution completed.", test_run=True)

if __name__ == "__main__":
    main()

cursor.close()  # Close the database cursor
db_connection.close()  # Close the database connection
