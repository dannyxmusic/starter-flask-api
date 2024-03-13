from flask import Flask, request
import 

app = Flask(__name__)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        # Access form fields from request.form
        form_id = request.form.get('formID')
        submission_id = request.form.get('submissionID')
        webhook_url = request.form.get('webhookURL')
        pretty_data = request.form.get('pretty')

        # Define a regular expression pattern to match each question-response pair
        pattern = r',\s*([^:,]+):([^:,]+)'

        # Extract question-response pairs using the regular expression
        pairs = re.findall(pattern, pretty_data)

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
