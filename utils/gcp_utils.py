import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # Using SSL port
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL_SENDER or not EMAIL_PASSWORD:
    raise ValueError("EMAIL_SENDER and EMAIL_PASSWORD must be set as environment variables.")

# OAuth 2.0 Client Secret File
CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE")

if not CLIENT_SECRET_FILE or not os.path.exists(CLIENT_SECRET_FILE):
    raise FileNotFoundError(f"Client secret file not found: {CLIENT_SECRET_FILE}")

# Scopes for Google APIs (Google Workspace Only)
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']

# Authenticate using OAuth 2.0
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
credentials = flow.run_local_server(port=0)

print("Access Token Generated:", credentials.token)

# Initialize Google Admin SDK
admin_service = build('admin', 'directory_v1', credentials=credentials)

def send_student_email(personal_email, university_email, first_name, last_name, password):
    """Sends an email to the student's personal email with their new Google Workspace login details."""
    subject = "Your Google Workspace Account Has Been Created"
    body = f"""
    Hello {first_name} {last_name},

    Your Google Workspace account has been successfully created.

    **Login Email:** {university_email}  
    **Temporary Password:** {password}  

    Please log in to Google Admin Console (https://admin.google.com/) and change your password immediately.

    Regards,  
    University Admin  
    """
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = personal_email

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, personal_email, msg.as_string())
            print(f"Email sent to: {personal_email}")
    except Exception as e:
        print(f"Error sending email to {personal_email}: {e}")

def update_google_workspace_user(email, first_name, last_name, recovery_email):
    """Updates user details in Google Workspace."""
    try:
        user_info = {
            "name": {"givenName": first_name, "familyName": last_name},
            "recoveryEmail": recovery_email,
        }
        admin_service.users().update(userKey=email, body=user_info).execute()
        print(f"User {email} updated successfully.")
        return True
    except Exception as e:
        print(f"Error updating user {email}: {e}")
        return False

def reset_google_workspace_password(email):
    """Resets a user's password in Google Workspace."""
    new_password = "NewPwd#1234"
    try:
        user_info = {"password": new_password}
        admin_service.users().update(userKey=email, body=user_info).execute()
        print(f"Password for {email} reset successfully.")
        return new_password
    except Exception as e:
        print(f"Error resetting password for {email}: {e}")
        return None

def suspend_google_workspace_user(email, suspend=True):
    """Suspends or activates a user in Google Workspace."""
    try:
        user_info = {"suspended": suspend}
        admin_service.users().update(userKey=email, body=user_info).execute()
        action = "suspended" if suspend else "activated"
        print(f"User {email} {action} successfully.")
        return True
    except Exception as e:
        print(f"Error updating user suspension status for {email}: {e}")
        return False

def delete_google_workspace_user(email):
    """Deletes a user from Google Workspace."""
    try:
        admin_service.users().delete(userKey=email).execute()
        print(f"User {email} deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting user {email}: {e}")
        return False

def create_google_workspace_user(first_name, last_name, personal_email):
    """Creates a Google Workspace user under the organization."""
    first_name = first_name.strip().lower().replace(" ", "")
    last_name = last_name.strip().lower().replace(" ", "")
    university_email = f"{first_name}.{last_name}@data-lab.site"
    temp_password = "DefaultPwd#123"

    user_info = {
        "name": {"givenName": first_name.capitalize(), "familyName": last_name.capitalize()},
        "primaryEmail": university_email,
        "password": temp_password,
        "orgUnitPath": "/",
        "recoveryEmail": personal_email.strip()
    }

    print(f"Creating Google Workspace user: {university_email} with payload:\n{user_info}")

    try:
        response = admin_service.users().insert(body=user_info).execute()
        print(f"Google Workspace Account Created: {university_email}\nResponse: {response}")
        send_student_email(personal_email, university_email, first_name.capitalize(), last_name.capitalize(), temp_password)
        return university_email
    except Exception as e:
        print(f"Error creating Google Workspace Account for {university_email}: {e}")
        return None

def list_google_workspace_users():
    """Fetches a list of all users in the Google Workspace."""
    try:
        results = admin_service.users().list(customer='my_customer', maxResults=500, orderBy='email').execute()
        users = results.get('users', [])
        if not users:
            print("No users found.")
            return []
        print(f"Found {len(users)} users in Google Workspace.")
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def create_google_workspace_users_from_file(file_path):
    """Reads a CSV or Excel file and creates Google Workspace accounts for students."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        print("Unsupported file format. Please upload a .csv or .xlsx file.")
        return

    required_columns = ["First Name", "Last Name", "Personal Email"]
    if not all(col in df.columns for col in required_columns):
        print("Missing required columns: 'First Name', 'Last Name', 'Personal Email'")
        return

    print(f"Processing {len(df)} students for Google Workspace account creation...")

    for _, student in df.iterrows():
        first_name = student['First Name']
        last_name = student['Last Name']
        personal_email = student['Personal Email']
        create_google_workspace_user(first_name, last_name, personal_email)

    print("Bulk Google Workspace User Creation Completed.")
