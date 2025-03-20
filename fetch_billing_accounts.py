from googleapiclient.discovery import build
from google.oauth2 import service_account

# Define the path to your service account JSON file
CREDENTIALS_PATH = "/Users/vedanth/Desktop/projects/admin gcp/Administrative-Google-Cloud-Platform/case-study-446714-da2b23dcbb83.json"

# Authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

# Initialize the Cloud Billing API service
billing_service = build("cloudbilling", "v1", credentials=credentials)

try:
    # Fetch the list of all billing accounts
    request = billing_service.billingAccounts().list()
    response = request.execute()
    
    # Print the response (list of billing accounts)
    print(response)
except Exception as e:
    print(f"Error: {e}")
