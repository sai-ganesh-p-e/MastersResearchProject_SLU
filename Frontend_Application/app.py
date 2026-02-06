from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector as mariadb
import bcrypt
import pyotp
import os
import qrcode
import io
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "team6@MRP",
    "database": "allyUserData"
}

LOG_FILE_PATH = "/home/mshrinivasan/login_log.txt"
TESTRUN_LOG_PATH = "/home/mshrinivasan/testrun-log.txt"

def log_event(event, test_run=False):
    log_file = TESTRUN_LOG_PATH if test_run else LOG_FILE_PATH
    with open(log_file, "a") as file:
        file.write(f"{datetime.now()} - {event}\n")

def get_db_connection():
    return mariadb.connect(**DB_CONFIG)

def get_user_credentials(username):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT password FROM Customers WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None

def verify_password(entered, stored):
    return bcrypt.checkpw(entered.encode(), stored.encode())

def get_totp_secret(username):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT totp_secret FROM Customers WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None

def get_backup_code(username):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT backup_code FROM Customers WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None

def generate_qr_code(username, secret):
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name="Ally Bank")
    qr = qrcode.make(uri)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()

def save_totp_credentials(username, secret, backup_code):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE Customers SET totp_secret=%s, backup_code=%s WHERE username=%s",
                   (secret, backup_code, username))
    db.commit()
    cursor.close()
    db.close()

def get_customer_info(username):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Customers WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        stored_password = get_user_credentials(username)

        if stored_password and verify_password(password, stored_password):
            session["username"] = username
            session["failed_attempts"] = 0
            backup_code = get_backup_code(username)
            if backup_code:
                return redirect(url_for("totp_auth"))
            else:
                return redirect(url_for("totp_alert"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/totp-alert")
def totp_alert():
    return render_template("totp_alert.html")

@app.route("/totp-alert-choice", methods=["POST"])
def totp_alert_choice():
    choice = request.form.get("choice")
    return redirect(url_for("totp_setup")) if choice == "yes" else redirect(url_for("customer"))

@app.route("/totp-setup", methods=["GET", "POST"])
def totp_setup():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    if request.method == "POST":
        entered_backup = request.form.get("confirm_backup", "").strip()
        if entered_backup == session.get("generated_backup_code"):
            # Always update database with new credentials
            save_totp_credentials(username, session["secret"], session["generated_backup_code"])
            return redirect(url_for("totp_auth"))
        else:
            return render_template("totp_setup.html", error="Incorrect backup code. Try again.", qr=session["qr_code"], secret=session["secret"], backup=session["generated_backup_code"])
    secret = pyotp.random_base32()
    backup = os.urandom(8).hex()
    qr = generate_qr_code(username, secret)
    session.update(secret=secret, generated_backup_code=backup, qr_code=qr)
    return render_template("totp_setup.html", qr=qr, secret=secret, backup=backup)

@app.route("/totp-auth", methods=["GET", "POST"])
def totp_auth():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    secret = get_totp_secret(username)
    if request.method == "POST":
        entered_code = request.form["totp"]
        totp = pyotp.TOTP(secret)
        if totp.verify(entered_code):
            session["failed_attempts"] = 0
            return redirect(url_for("customer"))
        session["failed_attempts"] = session.get("failed_attempts", 0) + 1
        if session["failed_attempts"] >= 3:
            return redirect(url_for("backup_prompt"))
        return render_template("totp_auth.html", error="Invalid code. Try again.")
    return render_template("totp_auth.html")

@app.route("/backup-prompt", methods=["GET", "POST"])
def backup_prompt():
    if request.method == "POST":
        entered = request.form["backup"]
        if entered == session.get("generated_backup_code") or entered == get_backup_code(session["username"]):
            session["failed_attempts"] = 0
            return redirect(url_for("totp_setup"))
        return render_template("backup_prompt.html", error="Invalid backup code.")
    return render_template("backup_prompt.html")

@app.route("/customer")
def customer():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    customer_info = get_customer_info(username)
    backup_code = get_backup_code(username)
    totp_complete = bool(backup_code)
    return render_template("customer.html", info=customer_info, show_alert=not totp_complete)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(debug=True)