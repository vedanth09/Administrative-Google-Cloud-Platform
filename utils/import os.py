from googleapiclient.discovery import build
from google.oauth2 import service_account

# Define Service Account JSON File Path
CREDENTIALS_PATH = "/Users/vedanth/Desktop/projects/admin gcp/Administrative-Google-Cloud-Platform/case-study-446714-da2b23dcbb83.json"

# Load credentials
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

# Initialize GCP Billing API
billing_service = build('cloudbilling', 'v1', credentials=credentials)

# Fetch Billing Accounts
try:
    request = billing_service.billingAccounts().list()
    response = request.execute()
    print(response)
except Exception as e:
    print(f"ERROR: {e}")
