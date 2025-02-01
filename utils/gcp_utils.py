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
SMTP_PORT = 465  # Changed to SSL port
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Ensure email configurations are set
if not EMAIL_SENDER or not EMAIL_PASSWORD:
    raise ValueError("EMAIL_SENDER and EMAIL_PASSWORD must be set as environment variables.")

# OAuth 2.0 Client Secret File
CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE")

# Ensure the client secret file exists
if not CLIENT_SECRET_FILE or not os.path.exists(CLIENT_SECRET_FILE):
    raise FileNotFoundError(f"Client secret file not found: {CLIENT_SECRET_FILE}")

# Scopes for Google APIs (Google Workspace Only)
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user'
]

# Authenticate using OAuth 2.0
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
credentials = flow.run_local_server(port=0)

# Print the access token for debugging
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
    msg["To"] = personal_email  # Now sending to personal email

    try:
        # Use SSL instead of STARTTLS
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, personal_email, msg.as_string())  # Sending to personal email
            print(f"Email sent to: {personal_email}")
    except Exception as e:
        print(f"Error sending email to {personal_email}: {e}")

def create_google_workspace_user(first_name, last_name, personal_email):
    """Creates a Google Workspace user under the organization."""
    first_name = first_name.strip().lower().replace(" ", "")  # Remove spaces & lowercase
    last_name = last_name.strip().lower().replace(" ", "")  # Remove spaces & lowercase
    university_email = f"{first_name}.{last_name}@data-lab.site"
    temp_password = "DefaultPwd#123"

    user_info = {
        "name": {"givenName": first_name.capitalize(), "familyName": last_name.capitalize()},
        "primaryEmail": university_email,
        "password": temp_password,
        "orgUnitPath": "/",
        "recoveryEmail": personal_email.strip()  # Personal email is required
    }

    print(f"Creating Google Workspace user: {university_email} with payload:\n{user_info}")  # Debugging

    try:
        response = admin_service.users().insert(body=user_info).execute()
        print(f"Google Workspace Account Created: {university_email}\nResponse: {response}")  # Debugging
        send_student_email(personal_email, university_email, first_name.capitalize(), last_name.capitalize(), temp_password)
        return university_email
    except Exception as e:
        print(f"Error creating Google Workspace Account for {university_email}: {e}")
        return None

def create_google_workspace_users_from_file(file_path):
    """Reads a CSV or Excel file and creates Google Workspace accounts for students."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Determine file format
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        print("Unsupported file format! Please upload a .csv or .xlsx file.")
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

        # Create Google Workspace User
        create_google_workspace_user(first_name, last_name, personal_email)

    print("Bulk Google Workspace User Creation Completed!")
