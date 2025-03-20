import subprocess
import json
from flask import Blueprint, request, render_template, jsonify

# Initialize Flask Blueprint
billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/gcp/billing', methods=['GET'])
def billing_page():
    """Render the Billing Page."""
    return render_template('billing.html')

@billing_bp.route('/gcp/billing/accounts', methods=['GET'])
def list_billing_accounts():
    """Fetch all linked billing accounts using gcloud command."""
    try:
        result = subprocess.run(
            ["gcloud", "beta", "billing", "accounts", "list", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )

        print("DEBUG: Raw GCloud Response:", result.stdout)  # Debug log

        # Ensure JSON output is valid
        try:
            billing_accounts = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print("ERROR: JSON Parsing Failed:", str(e))
            return render_template("billing.html", error="Invalid JSON response from GCP.")

        # Ensure it's a list format
        if not isinstance(billing_accounts, list):
            return render_template("billing.html", error="Unexpected response format from GCP.")

        return render_template("billing.html", billing_accounts=billing_accounts)

    except subprocess.CalledProcessError as e:
        return render_template("billing.html", error=f"Failed to list billing accounts: {e.stderr}")

@billing_bp.route('/gcp/billing/account-details', methods=['GET'])
def get_billing_account_details():
    """Fetch details for a specific billing account using gcloud command."""
    billing_account_id = request.args.get("billing_account_id")
    if not billing_account_id:
        return render_template("billing_details.html", error="Billing account ID is required.")

    try:
        result = subprocess.run(
            ["gcloud", "beta", "billing", "accounts", "describe", billing_account_id, "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )

        print("DEBUG: Raw Billing Account Details:", result.stdout)  # Debug log

        # Ensure JSON output is valid
        try:
            account_details = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print("ERROR: JSON Parsing Failed:", str(e))
            return render_template("billing_details.html", error="Invalid JSON response from GCP.")

        return render_template("billing_details.html", account=account_details)

    except subprocess.CalledProcessError as e:
        return render_template("billing_details.html", error=f"Failed to fetch billing details: {e.stderr}")