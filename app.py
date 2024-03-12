from flask import Flask, request
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, daniel!'


@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Check if the request contains form data
    if request.method == 'POST':
        # Parse form data from the request
        form_data = request.form.to_dict()

        # Process the form data
        # Here you can perform any necessary operations with the form data,
        # such as saving it to a database, sending notifications, etc.

        # Example: Print the form data to the console
        print("Received form data:")
        print(form_data)

        # Return a response to indicate successful processing
        return 'Form data received successfully!', 200
    else:
        # Return an error response for unsupported request methods
        return 'Method not allowed', 405


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
