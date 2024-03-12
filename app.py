from flask import Flask, request
import subprocess

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, daniel!'


@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Check if the request contains form data
    if request.method == 'POST':
        # Read the JSON data from the request
        json_string = request.data.decode('utf-8')

        # Execute the test.py script and capture its output
        result = subprocess.run(['python', 'test.py'], input=json_string.encode(
            'utf-8'), capture_output=True, text=True)

        # Return the output of test.py as the response
        return result.stdout, 200
    else:
        # Return an error response for unsupported request methods
        return 'Method not allowed', 405


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
