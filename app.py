from flask import Flask, request

app = Flask(__name__)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        # Access form fields from request.form
        form_id = request.form.get('formID')
        submission_id = request.form.get('submissionID')
        webhook_url = request.form.get('webhookURL')
        pretty_data = request.form.get('pretty')

        # Split the pretty_data string by commas to separate the pairs
        pairs = pretty_data.split(', ')

        # Initialize an empty dictionary to store the question-response pairs
        parsed_data = {}

        # Iterate through the pairs
        for pair in pairs:
            # Split each pair by the colon to extract the key-value pair
            key, value = pair.split(':', 1)  # Split by first colon only
            # Remove any leading/trailing whitespace from the key and value
            key = key.strip()
            value = value.strip()
            # Add the key-value pair to the dictionary
            parsed_data[key] = value

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
