# Enhancing Customer Authentication with Time-Based One-Time Password (TOTP) Security

This project is a Linux-based secure banking platform using **Flask**, **MariaDB**, and **TOTP (Time-based One-Time Password)**. It includes a frontend web app and backend scripts for secure authentication, user data management, and TOTP-based 2FA.

---

## 📌 Prerequisites & Setup Guide

Before running this project, follow the steps below to set up your environment.

### 🖥️ 1. Virtual Machine Setup

1. **Install Oracle VirtualBox**  
   Download and install [Oracle VirtualBox](https://www.virtualbox.org/) to create and manage virtual machines.

2. **Download RHEL 9.5 ISO**  
   Get the ISO image for Red Hat Enterprise Linux 9.5 from the [Red Hat Customer Portal](https://access.redhat.com/downloads).

3. **RHEL Subscription**  
   Ensure you have an active RHEL subscription.  
   > 💡 Alternatively, you can use **CentOS 8 or 9**, though installation commands may slightly differ.

4. **Create a RHEL 9.5 Virtual Machine**  
   Use VirtualBox to create a new VM and install RHEL 9.5 using the ISO.

---

### ⚙️ 2. Install Required Tools & Dependencies

After booting into your RHEL 9.5 VM, install all necessary tools using the following commands:

#### 📦 System Updates & Git

```bash
# Update system packages
sudo dnf update -y

# Install Git
sudo dnf install -y git

# Check Git version
git --version

# Clone the project repository
git clone https://github.com/mohanramshrinivasan/MastersResearchProject_SLU.git
```

#### 🐍 Python & Flask Environment

```bash
# Install Python 3
sudo dnf install -y python3

# Check Python version
python3 --version

# Install pip for Python 3
sudo dnf install -y python3-pip

# Check pip version
pip3 --version

# Install Flask (web framework)
pip3 install Flask
flask --version
```

#### 🔐 Python Security & TOTP Libraries

```bash
# Install bcrypt for password hashing
pip3 install bcrypt

# Install pyotp for TOTP 2FA
pip3 install pyotp

# Install qrcode (for QR generation)
pip3 install qrcode[pil]

# Install pytz for timezone support
pip3 install pytz
```

---

### 🛢️ 3. Install and Configure MariaDB

```bash
# Install MariaDB server
sudo dnf install -y mariadb-server

# Enable MariaDB to start on boot
sudo systemctl enable mariadb

# Start MariaDB now
sudo systemctl start mariadb

# Check MariaDB status
sudo systemctl status mariadb
```

#### 🔐 Secure MariaDB Installation

Run the secure setup tool:

```bash
sudo mysql_secure_installation
```

When prompted, use the following responses:

- Set root password? → **Y** (Use `team6@MRP`)
- Remove anonymous users? → **Y**
- Disallow root login remotely? → **Y**
- Remove test database? → **Y**
- Reload privilege tables now? → **Y**

---

### 🗃️ 4. Create Database and Table

```bash
# Login to MariaDB with root credentials
mysql -u root -p
```

Then run the following SQL commands inside the MariaDB shell:

```sql
-- Create the database
CREATE DATABASE allyUserData;

-- Switch to the new database
USE allyUserData;

-- Create the Customers table
CREATE TABLE Customers (
  username VARCHAR(50) NOT NULL PRIMARY KEY,
  firstname VARCHAR(100) NOT NULL,
  lastname VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL,
  dob DATE NOT NULL,
  totp_secret VARCHAR(64),
  backup_code VARCHAR(64),
  bank_account_number VARCHAR(20) NOT NULL UNIQUE,
  account_balance DECIMAL(10,2) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  address VARCHAR(255) NOT NULL,
  mobile_number VARCHAR(15) NOT NULL UNIQUE,
  account_type VARCHAR(50) NOT NULL
);

-- Check table structure
DESCRIBE Customers;

-- Optional: View data in table
SELECT * FROM Customers;
```

---

### 🔗 5. Install MySQL Connector for Python

```bash
# Install connector to interact with MariaDB from Python
pip3 install mysql-connector-python
```

---

## 🚀 Running the Project Scripts

Navigate to the appropriate project folders and execute the following scripts:

> 💡 Make sure you’re in the correct directory: `/root/MastersResearchProject_SLU/`

---

### 1. 🔧 Start the Web App

```bash
python3 Frontend_Application/app.py
```

This launches the Flask-based web UI for login and user interaction.

---

### 2. ✅ Check MariaDB-Python Connectivity

```bash
python3 Backend_Application/mariaDBConCheck.py
```

This verifies that Python can successfully connect to the MariaDB database.

---

### 3. 👤 Create Test Users

```bash
python3 Backend_Application/userCreation.py
```

This script will generate user records directly into the `Customers` table via terminal prompts.

---

### 4. 🔐 Trigger TOTP Setup Script

```bash
python3 Backend_Application/totpSetup.py
```

This script sets up TOTP 2FA and generates a QR code that can be scanned with an app like Google Authenticator.

---

## 🙌 Contributions

Feel free to clone the repo, run the scripts, and modify the logic as needed. Contributions to improve functionality or security are welcome!

---

## 📬 Contact

If you encounter issues or need guidance, feel free to open an issue or reach out via the GitHub repository.
