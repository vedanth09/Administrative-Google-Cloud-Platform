from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pandas as pd
import os
from utils.gcp_utils import (  # OAuth for Google Workspace
    create_google_workspace_user,
    list_google_workspace_users,
    update_google_workspace_user,
    reset_google_workspace_password,
    suspend_google_workspace_user,
    delete_google_workspace_user,
)
from utils.gcp_billing_manager import billing_bp  # Service Account for GCP Billing
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debugging: Print Python path & service account file
import sys
print(f"DEBUG: Running Flask with Python: {sys.executable}")
print(f"DEBUG: SERVICE_ACCOUNT_FILE = {os.getenv('SERVICE_ACCOUNT_FILE')}")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register the Billing API routes (GCP Billing)
app.register_blueprint(billing_bp, url_prefix='/gcp')

# Mock authentication credentials
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'vedanth.balakrishna2001@gmail.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Vedanth@123')

@app.route('/', methods=['GET', 'POST'])
def login():
    """Login Page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['user'] = email
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

@app.route('/home', methods=['GET'])
def home():
    """Home Page after Login"""
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        users = list_google_workspace_users()
        total_users = len(users)
        total_admins = len([user for user in users if user.get('isAdmin')])
        suspended_users = len([user for user in users if user.get('suspended')])
        active_users = total_users - suspended_users

        return render_template(
            'index.html',
            total_users=total_users,
            total_admins=total_admins,
            suspended_users=suspended_users,
            active_users=active_users,
        )
    except Exception as e:
        flash(f"Error fetching user statistics: {str(e)}", "danger")
        return render_template('index.html', total_users=0, total_admins=0, suspended_users=0, active_users=0)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handles CSV uploads and creates Google Workspace users."""
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded. Please select a file.", "danger")
            return redirect(url_for('upload_file'))

        file = request.files['file']

        if file.filename == '' or not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            flash("Invalid file type. Only CSV and Excel files are allowed.", "danger")
            return redirect(url_for('upload_file'))

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath) if file.filename.endswith('.csv') else pd.read_excel(filepath)
            required_columns = {"First Name", "Last Name", "Personal Email"}

            if not required_columns.issubset(df.columns):
                flash("Invalid file format. Ensure required columns are present.", "danger")
                return redirect(url_for('upload_file'))

            for _, student in df.iterrows():
                create_google_workspace_user(
                    student['First Name'],
                    student['Last Name'],
                    student['Personal Email']
                )

            flash("Users created successfully!", "success")
        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")

    return render_template('upload.html')

@app.route('/users', methods=['GET'])
def list_users():
    """Displays all Google Workspace users."""
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        users = list_google_workspace_users()
        return render_template('users.html', users=users)
    except Exception as e:
        flash(f"Error fetching users: {str(e)}", "danger")
        return redirect(url_for('home'))

@app.route('/users/reset-password', methods=['POST'])
def reset_password():
    """Resets a user's password."""
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    email = request.json.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        new_password = reset_google_workspace_password(email)
        return jsonify({"message": f"Password reset successfully for {email}!", "password": new_password})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/bulk-suspend', methods=['POST'])
def bulk_suspend_users():
    """Bulk Suspend or Activate Users."""
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    request_data = request.json
    emails = request_data.get('emails', [])
    action = request_data.get('action', '').strip().lower()

    if not emails:
        return jsonify({"error": "No users selected for suspension"}), 400

    if action not in ['suspend', 'activate']:
        return jsonify({"error": "Invalid action. Expected 'suspend' or 'activate'"}), 400

    errors = []
    is_suspend = (action == 'suspend')
    for email in emails:
        success = suspend_google_workspace_user(email, is_suspend)
        if not success:
            errors.append(email)

    if errors:
        return jsonify({"message": "Some users could not be suspended/activated", "failed": errors}), 500
    return jsonify({"message": f"Selected users {'suspended' if is_suspend else 'activated'} successfully!"})

@app.route('/users/bulk-delete', methods=['POST'])
def bulk_delete_users():
    """Deletes multiple users from Google Workspace."""
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    emails = request.json.get('emails', [])

    if not emails:
        return jsonify({"error": "No users selected for deletion"}), 400

    errors = []
    for email in emails:
        print(f"DEBUG: Sending delete request for user: {email}") 
        success = delete_google_workspace_user(email)
        if not success:
            errors.append(email)

    if errors:
        return jsonify({"message": "Some users could not be deleted", "failed": errors}), 500
    return jsonify({"message": "Selected users deleted successfully!"})

@app.route('/logout')
def logout():
    """Logs out the admin."""
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)