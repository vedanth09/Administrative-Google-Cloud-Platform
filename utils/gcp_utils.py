from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from google.cloud import bigquery

# Load credentials
SERVICE_ACCOUNT_FILE = 'service_account.json'
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/admin.directory.user',
                                  'https://www.googleapis.com/auth/cloud-platform'])

# Google Workspace API (Admin SDK)
admin_service = build('admin', 'directory_v1', credentials=credentials)

# BigQuery Client
bigquery_client = bigquery.Client(credentials=credentials)

def create_student_account(first_name, last_name, university_email, personal_email):
    """Creates a student account in Google Workspace"""
    user_info = {
        "name": {"givenName": first_name, "familyName": last_name},
        "password": "DefaultPassword123",
        "primaryEmail": university_email,
        "recoveryEmail": personal_email,
    }
    try:
        admin_service.users().insert(body=user_info).execute()
        print(f"Account created: {university_email}")
    except Exception as e:
        print(f"Error creating account: {e}")

def upload_to_bigquery(first_name, last_name, university_email, personal_email):
    """Uploads student data to BigQuery"""
    dataset_id = 'student_data'
    table_id = 'students'

    table_ref = bigquery_client.dataset(dataset_id).table(table_id)
    rows_to_insert = [{"first_name": first_name, "last_name": last_name, "university_email": university_email, "personal_email": personal_email}]
    
    errors = bigquery_client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print(f"BigQuery Insert Error: {errors}")
    else:
        print(f"Data inserted for {university_email}")

def delete_users(emails):
    """Deletes student accounts in Google Workspace"""
    for email in emails:
        try:
            admin_service.users().delete(userKey=email).execute()
            print(f"Deleted: {email}")
        except Exception as e:
            print(f"Error deleting {email}: {e}")
