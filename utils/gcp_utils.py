import os
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

load = load_dotenv()
# Load Google Cloud Service Account Credentials
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Ensure the service account file exists
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")

# Authenticate with Google APIs
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=[
        'https://www.googleapis.com/auth/admin.directory.user',
        'https://www.googleapis.com/auth/cloud-platform'
    ])

# Initialize Google Admin SDK and Cloud Resource Manager
admin_service = build('admin', 'directory_v1', credentials=credentials)
cloud_resource_manager = build('cloudresourcemanager', 'v1', credentials=credentials)

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL_SENDER or not EMAIL_PASSWORD:
    raise ValueError("EMAIL_SENDER and EMAIL_PASSWORD must be set as environment variables.")

def send_student_email(student_email, first_name, last_name, password):
    """Sends an email to the student with login details."""
    subject = "Your Google Cloud Account Has Been Created"
    body = f"""
    Hello {first_name} {last_name},

    Your Google Cloud account has been successfully created.

    Login Email: {student_email}
    Temporary Password: {password}

    Please log in to Google Cloud Console (https://console.cloud.google.com/) and change your password immediately.

    Regards,
    University Admin
    """

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = student_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, student_email, msg.as_string())
        server.quit()
        print(f"Email sent to: {student_email}")
    except Exception as e:
        print(f"Error sending email to {student_email}: {e}")

def create_gcp_user(first_name, last_name, personal_email):
    """Creates a Google Cloud Identity user under the organization."""
    university_email = f"{first_name.lower()}.{last_name.lower()}@srh-heidelberg.org"
    temp_password = "DefaultPassword123"

    user_info = {
        "name": {"givenName": first_name, "familyName": last_name},
        "primaryEmail": university_email,
        "password": temp_password,
        "orgUnitPath": "/",
        "recoveryEmail": personal_email  # Fixed field name
    }

    try:
        admin_service.users().insert(body=user_info).execute()
        print(f"GCP Account Created: {university_email}")

        send_student_email(university_email, first_name, last_name, temp_password)

        return university_email
    except Exception as e:
        print(f"Error creating GCP Account for {university_email}: {e}")
        return None

def assign_gcp_roles(university_email):
    """Assigns IAM roles to the student so they can access Google Cloud."""
    organization_id = "organizations/1053449573907"  # Fixed organization ID format
    roles = ["roles/viewer"]

    try:
        policy = cloud_resource_manager.organizations().getIamPolicy(resource=organization_id).execute()

        for role in roles:
            if any(binding["role"] == role and f"user:{university_email}" in binding["members"] for binding in policy.get("bindings", [])):
                print(f"{university_email} already has role: {role}")
                continue  

            policy["bindings"].append({
                "role": role,
                "members": [f"user:{university_email}"]
            })

        request = cloud_resource_manager.organizations().setIamPolicy(
            resource=organization_id, body={"policy": policy})
        request.execute()

        print(f"IAM Roles Assigned to {university_email}")

    except Exception as e:
        print(f"Error assigning IAM roles for {university_email}: {e}")

def create_and_assign_gcp_users(file_path):
    """Reads a CSV or Excel file and creates GCP accounts for students."""
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

    for _, student in df.iterrows():
        first_name = student['First Name']
        last_name = student['Last Name']
        personal_email = student['Personal Email']

        university_email = create_gcp_user(first_name, last_name, personal_email)

        if university_email:
            assign_gcp_roles(university_email)

    print("Bulk GCP User Creation Completed!")
