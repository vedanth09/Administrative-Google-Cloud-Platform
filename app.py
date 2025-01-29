from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from utils.gcp_utils import create_gcp_user, assign_gcp_roles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Home Page"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handles CSV and Excel uploads and processes GCP account creation."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded. Please select a file.", "danger")
            return redirect(url_for('upload_file'))

        file = request.files['file']

        if file.filename == '':
            flash("No selected file. Please choose a file to upload.", "danger")
            return redirect(url_for('upload_file'))

        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            flash("Invalid file type. Only CSV and Excel (.xlsx) files are allowed.", "danger")
            return redirect(url_for('upload_file'))

        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Load CSV or Excel file
            df = pd.read_csv(filepath) if file.filename.endswith('.csv') else pd.read_excel(filepath)

            # Validate if required columns exist
            required_columns = {"First Name", "Last Name", "Personal Email"}
            if not required_columns.issubset(df.columns):
                flash("Invalid file format. Ensure the file has 'First Name', 'Last Name', and 'Personal Email' columns.", "danger")
                return redirect(url_for('upload_file'))

            students = df.to_dict(orient='records')

            created_accounts = 0
            for student in students:
                first_name = student['First Name']
                last_name = student['Last Name']
                personal_email = student['Personal Email']

                # Create GCP Account
                university_email = create_gcp_user(first_name, last_name, personal_email)

                if university_email:
                    assign_gcp_roles(university_email)
                    created_accounts += 1

            flash(f"{created_accounts} GCP accounts created successfully!", "success")
            return redirect(url_for('upload_file'))

        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")
            return redirect(url_for('upload_file'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
