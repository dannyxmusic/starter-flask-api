from flask import Flask, request
import json

app = Flask(__name__)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Collect payload data from the request
    pretty = request.form.get('pretty')
    formID = request.form.get('formID')
    submissionID = request.form.get('submissionID')
    webhookURL = request.form.get('webhookURL')
    formTitle = request.form.get('formTitle')

    # Create a dictionary to store the data
    payload_data = {
        'pretty': pretty,
        'formID': formID,
        'submissionID': submissionID,
        'webhookURL': webhookURL,
        'formTitle': formTitle
    }

    # Convert dictionary to JSON format
    json_data = json.dumps(payload_data, indent=4)

    # Print the JSON data
    print(json_data)

    # Optionally, you can process or respond to the payload data here

    # Return a response if needed
    return json_data, 200


if __name__ == '__main__':
    app.run(debug=True)
