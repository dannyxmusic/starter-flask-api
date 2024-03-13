import os
import re
import requests
from flask import Flask, abort, request

app = Flask(__name__)

# Define MongoDB Atlas API URL
MONGODB_API_URL = os.getenv("MONGODB_API_URL")
MONGODB_API_KEY = os.getenv("MONGODB_API_KEY")


@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        # Check if the request method is POST
        if request.method != 'POST':
            abort(405)  # Method not allowed

        # Check if the request contains JSON data
        if not request.is_json:
            abort(400)  # Bad request

        # Parse JSON data from the request
        data = request.get_json()

        # Extract specific fields
        form_id = data.get('formID', None)
        submission_id = data.get('submissionID', None)
        webhook_url = data.get('webhookURL', None)
        pretty_info = data.get('pretty', None)

        # Define a regular expression pattern to match each question-response pair
        pattern = r'([^:,]+):([^:,]+)'

        # Extract question-response pairs using the regular expression
        pairs = re.findall(pattern, pretty_info)

        # Initialize an empty dictionary to store the question-response pairs
        parsed_data = {}

        # Iterate through the pairs
        for pair in pairs:
            # Remove any leading/trailing whitespace from the question and response
            question = pair[0].strip()
            response = pair[1].strip()
            # Add the question-response pair to the dictionary
            parsed_data[question] = response

        # Add formID, submissionID, and webhookURL to the parsed data
        parsed_data['formID'] = form_id
        parsed_data['submissionID'] = submission_id
        parsed_data['webhookURL'] = webhook_url

        # Make API request to MongoDB Atlas API
        response = requests.post(
            f"{MONGODB_API_URL}/insertOne",
            json={
                "dataSource": "testimonialGenerator",
                "database": "tpc_survey_f1",
                "collection": "cyclic_server",
                "document": parsed_data
            },
            headers={"Content-Type": "application/json",
                     "api-key": MONGODB_API_KEY}
        )

        # Check if the MongoDB API request was successful
        if response.status_code in [200, 201]:
            return "Data successfully inserted into MongoDB", response.status_code
        else:
            return f"Error inserting data into MongoDB: {response.text}", response.status_code

    except Exception as e:
        # Return an error response if there's an exception
        return f"Error processing request: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
