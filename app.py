from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        # Access form fields from request.form
        form_id = request.form.get('formID')
        submission_id = request.form.get('submissionID')
        webhook_url = request.form.get('webhookURL')
        pretty_data = request.form.get('pretty')

        # Construct a dictionary with the form data
        data = {
            'formID': form_id,
            'submissionID': submission_id,
            'webhookURL': webhook_url,
            'prettyData': pretty_data
        }

        # Print the JSON data
        print(data)

        # Return a success response
        return 'Data received and printed as JSON successfully!'

    except Exception as e:
        # Log the error
        print('An error occurred:', e)
        # Return an error response
        return 'An error occurred while processing the data.', 500


if __name__ == '__main__':
    app.run(debug=True)
