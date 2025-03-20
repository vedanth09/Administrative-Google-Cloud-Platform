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
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.group.member'
]

# Authenticate using OAuth 2.0
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
credentials = flow.run_local_server(port=0)

print("Access Token Generated:", credentials.token)

# Initialize Google Admin SDK
admin_service = build('admin', 'directory_v1', credentials=credentials)

### 🛠️ EXISTING FUNCTIONS (UNCHANGED) ###

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
        print(f"DEBUG: Attempting to delete user {email}")  # 
        admin_service.users().delete(userKey=email).execute()
        print(f"DEBUG: User {email} deleted successfully.")  # 
        return True
    except Exception as e:
        print(f"ERROR: Failed to delete user {email}: {e}")  # 
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

###  NEWLY ADDED GROUP MANAGEMENT FUNCTIONS ###

def create_google_workspace_group(group_name, group_email, description=""):
    """Creates a new Google Workspace group."""
    try:
        group_body = {
            "email": group_email,
            "name": group_name,
            "description": description
        }
        response = admin_service.groups().insert(body=group_body).execute()
        print(f"Group '{group_name}' created successfully!")
        return response
    except Exception as e:
        print(f"Error creating group '{group_name}': {e}")
        return None

def add_user_to_group(user_email, group_email):
    """Adds a user to a Google Workspace group."""
    try:
        membership_body = {
            "email": user_email,
            "role": "MEMBER"
        }
        response = admin_service.members().insert(groupKey=group_email, body=membership_body).execute()
        print(f"User '{user_email}' added to group '{group_email}'.")
        return response
    except Exception as e:
        print(f"Error adding user '{user_email}' to group '{group_email}': {e}")
        return None

def remove_user_from_group(user_email, group_email):
    """Removes a user from a Google Workspace group."""
    try:
        response = admin_service.members().delete(groupKey=group_email, memberKey=user_email).execute()
        print(f"User '{user_email}' removed from group '{group_email}'.")
        return response
    except Exception as e:
        print(f"Error removing user '{user_email}' from group '{group_email}': {e}")
        return None

def delete_google_workspace_group(group_email):
    """Deletes a Google Workspace group."""
    try:
        response = admin_service.groups().delete(groupKey=group_email).execute()
        print(f"Group '{group_email}' deleted successfully.")
        return response
    except Exception as e:
        print(f"Error deleting group '{group_email}': {e}")
        return None
