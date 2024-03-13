from flask import Flask, request
import re

app = Flask(__name__)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        # Access form fields from request.form
        form_id = request.form.get('formID')
        submission_id = request.form.get('submissionID')
        webhook_url = request.form.get('webhookURL')
        pretty_data = request.form.get('pretty')

        # Split the data into key-value pairs
        pairs = [pair.split(':') for pair in pretty_data.split(', ')]

        # Create a dictionary from the pairs
        parsed_data = {key.strip(): value.strip() for key, value in pairs}

        # Add formID, submissionID, and webhookURL to the parsed data
        parsed_data['formID'] = form_id
        parsed_data['submissionID'] = submission_id
        parsed_data['webhookURL'] = webhook_url

        # Do whatever you need with the parsed data
        print('Parsed Data:', parsed_data)

        # Return a response if necessary
        return 'Data received and parsed successfully!'

    except Exception as e:
        # Log the error
        print('An error occurred:', e)
        # Return an error response
        return 'An error occurred while processing the data.', 500


if __name__ == '__main__':
    app.run(debug=True)
