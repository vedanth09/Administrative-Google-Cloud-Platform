from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from utils.gcp_utils import create_student_account, upload_to_bigquery, delete_users
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = '/Users/vedanth/Desktop/case-study-446714-0445861289fe.json'  # Change this to a secure key

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process file and create accounts
            df = pd.read_csv(filepath)
            students = df.to_dict(orient='records')

            for student in students:
                first_name = student['First Name']
                last_name = student['Last Name']
                personal_email = student['Personal Email']
                university_email = f"{first_name.lower()}.{last_name.lower()}@srh-heidelberg.org"
                
                # Create Google Account
                create_student_account(first_name, last_name, university_email, personal_email)

                # Upload to BigQuery
                upload_to_bigquery(first_name, last_name, university_email, personal_email)

            flash("Student accounts created successfully!", "success")
            return redirect(url_for('index'))
    
    return render_template('upload.html')

@app.route('/billing')
def billing():
    # Fetch billing data (to be implemented)
    return render_template('billing.html')

@app.route('/delete', methods=['POST'])
def delete_students():
    student_emails = request.form.getlist('selected_students')
    delete_users(student_emails)
    flash("Selected students deleted successfully!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
