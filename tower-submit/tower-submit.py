import os
import subprocess
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import json

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

def send_email(subject, body, to_email, from_email, password):
    password = os.getenv("GMAIL_PASSWORD")
    try:
        # Set up the SMTP server and port for SSL
        smtp_server = "smtp.gmail.com"
        smtp_port = 465  # SSL port

        # Create the email components
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # Add the email body
        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server using SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(from_email, password)  # Log in to the Gmail account
            server.sendmail(from_email, to_email, msg.as_string())  # Send the email
        
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

subject = "Test Email"
body = "This is a test email sent from Python!"
to_email = "sebastian.raemisch@cambrium.bio"
from_email = "ops@cambrium.bio"


# Endpoint to handle POST requests with form data and files
@app.route("/api/workflow/run", methods=["POST"])
def submit_workflow():
    try:
        # Parse arguments (form data)
        arguments = request.form.to_dict()
        # Print received arguments
        print(f"Arguments received: {arguments}")
        
        # Handle file uploads
        files = request.files.getlist('files')  # Get all uploaded files
        file_paths = []
        if files:
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)

            for file in files:
                filename = secure_filename(file.filename)
                file_location = os.path.join(upload_dir, filename)
                file.save(file_location)  # Save file to the server
                file_paths.append(file_location)

        # Run Nextflow pipeline in the background irrespective of files uploaded
        nextflow_command = ["nextflow", "run", "/Users/raemisch/projects/Cambrium-NextFlow-Design/main.nf", "-with-tower" , "-bucket-dir", arguments['bucket-dir'], "--use-gpu", arguments['use_gpu'], "-profile", arguments['profile'], "--mode", arguments['mode']]
        nextflow_command = arguments['cmd']
        process = subprocess.Popen(nextflow_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # Optionally, capture the output of the command (you could also log it if needed)
        stdout, stderr = process.communicate()
        print(f"Nextflow STDOUT: {stdout.decode()}")
        print(f"Nextflow STDERR: {stderr.decode()}")

        return jsonify({
            "message": "Workflow submitted successfully",
            "arguments": arguments,
            "files": file_paths,
            "nextflow_output": stdout.decode()
        })

    except Exception as e:
        return jsonify({
            "message": f"An error occurred: {str(e)}"
        }), 400


if __name__ == "__main__":
    app.run(debug=True)
