import json
import os
import subprocess
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import logging
import traceback
import time
from datetime import datetime
import requests

app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TowerAuth:
    def __init__(self, token, email):
        self.base_url = "http://localhost:8080"
        self.access_token = token
        self.email = email
        self.session = requests.Session()

    def verify_credentials(self):
        """Verify Tower credentials by attempting to login"""
        try:
            # Attempt login
            login_response = self.session.post(
                f"{self.base_url}/login",
                json={
                    'username': '@token',
                    'password': self.access_token
                },
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                allow_redirects=False
            )

            # Check for successful login (303 redirect to /auth?success=true)
            if login_response.status_code == 303 and 'success=true' in login_response.headers.get('Location', ''):
                # Follow redirect to get user info
                auth_response = self.session.get(
                    f"{self.base_url}/user",
                    headers={'Accept': 'application/json'},
                    allow_redirects=False
                )
                
                if auth_response.status_code == 200:
                    user_data = json.loads(auth_response.text)
                    if user_data['user']['email'] == self.email:
                        return True, "Credentials verified"
                    else:
                        return False, "Email address does not match token"
                
            return False, "Invalid credentials"
            
        except Exception as e:
            logger.error(f"Tower authentication error: {str(e)}")
            return False, f"Authentication error: {str(e)}"

@app.route("/api/workflow/run", methods=["POST"])
def submit_workflow():
    try:
        # Get Tower credentials from request
        tower_token = request.headers.get('Tower-Token')
        tower_email = request.headers.get('Tower-Email')
        
        if not tower_token or not tower_email:
            return jsonify({
                "message": "Both Tower-Token and Tower-Email headers are required"
            }), 401

        # Verify Tower credentials
        tower_auth = TowerAuth(tower_token, tower_email)
        is_valid, auth_message = tower_auth.verify_credentials()
        
        if not is_valid:
            return jsonify({
                "message": f"Tower authentication failed: {auth_message}"
            }), 401

        # Parse arguments (form data)
        arguments = request.form.to_dict()
        logger.info(f"Arguments received: {arguments}")
        
        # Validate required arguments
        if '-bucket-dir' not in arguments:
            return jsonify({"message": "bucket-dir is required"}), 400
        if '--mode' not in arguments:
            return jsonify({"message": "mode is required"}), 400

        # Handle file uploads
        files = request.files
        file_paths = []

        # Create unique job directory
        now = datetime.now()
        time_str = now.strftime("%Y%m%d_%H%M%S")
        millis = now.microsecond // 1000
        uid = f"{time_str}_{millis}"
        workdir = f"/home/ec2-user/jobs/job_{uid}"
        current_dir = os.getcwd()
        
        try:
            os.makedirs(workdir, exist_ok=True)
            logger.info(f"Created workdir: {workdir}")
            os.chdir(workdir)
            logger.info(f"chdir {os.getcwd()}")
        except Exception as e:
            logger.error(f"Directory error: {str(e)}")
            return jsonify({"message": f"Failed to create working directory: {str(e)}"}), 500

        # Process uploaded files
        if files:
            logger.info(f"Received {len(files)} files")
            for filename, file in files.items():
                sec_filename = secure_filename(filename)
                file_location = os.path.join(workdir, sec_filename)
                file.save(file_location)
                file_paths.append(file_location)
            logger.info(f"Saved files: {file_paths}")
        else:
            logger.info("No files received")

        # Construct and run Nextflow command
        nextflow_command = "nextflow run /home/ec2-user/Cambrium-NextFlow-Design/main.nf -with-tower"
        for key, value in arguments.items():
            nextflow_command += f" {key} {value}"

        logger.info(f"Running Nextflow command:\n {nextflow_command}")
        process = subprocess.Popen(
            nextflow_command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            shell=True,
            env={**os.environ, 'TOWER_ACCESS_TOKEN': tower_token}  # Pass token to Nextflow
        )

        # Wait briefly and check process status
        time.sleep(12)
        return_code = process.poll()
        os.chdir(current_dir)

        if return_code is not None:
            stdout, stderr = process.communicate()
            if return_code == 0:
                return jsonify({
                    "message": "Workflow started successfully (and finished quickly)",
                    "arguments": arguments,
                    "files": file_paths,
                    "nextflow_output": stdout.decode()
                }), 200
            else:
                return jsonify({
                    "message": "Workflow failed to start",
                    "arguments": arguments,
                    "files": file_paths,
                    "nextflow_error": f"{stdout.decode()}\n{stderr.decode()}"
                }), 500

        return jsonify({
            "message": f"Workflow started successfully in {workdir}",
            "arguments": arguments,
            "files": file_paths,
            "process_id": process.pid
        }), 202

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({
            "message": f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
