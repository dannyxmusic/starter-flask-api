from flask import Flask, request

app = Flask(__name__)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Collect payload data from the request
    payload_data = request.form.to_dict()

    # Print the payload data
    print(payload_data)

    # Optionally, you can process or respond to the payload data here

    # Return a response if needed
    return 'Payload received successfully!', 200


if __name__ == '__main__':
    app.run(debug=True)
