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
        form_data = request.form

        # Return a response to indicate successful processing
        return form_data, 200
    else:
        # Return an error response for unsupported request methods
        return 'Method not allowed', 405


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
