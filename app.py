from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB Atlas connection URI
MONGO_URI = os.environ.get('MONGO_URI')

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)

# Access the database and collection
db = client['tpc_survey_f1']
collection = db['cyclic_server']


def parse_pretty_data(pretty_data):
    # Define the list of questions
    questions = [
        "Please Enter your Email Address",
        "How would you rate the ease of transitioning and implementation to TPC's services from your previous payroll provider?",
        "How user-friendly do you find iSolved, TPC's HR and payroll software?",
        "Who was your previous Payroll Provider?",
        "How would you rate your satisfaction for TPC over your previous payroll provider?",
        "How would you rate your experience with TPC's customer service in addressing your inquiries and concerns?",
        "How many employees does your company currently process payroll for?",
        "How inclined are you to recommend Grant Stuart and TPC's services to another business?",
        "Please share your experience or any additional feedback you have regarding your experience with Grant Stuart and TPC."
    ]

    # Initialize a dictionary to store key-value pairs
    extracted_data = {}
    email = None

    # Iterate through each question
    for i in range(len(questions)):
        question = questions[i]
        # If it's the email question, extract and continue
        if "Please Enter your Email Address" in question:
            email = pretty_data.split(":")[1].strip().split(",")[0]
            continue

        # Find the index of the next question
        next_question_index = pretty_data.find(
            questions[i + 1]) if i < len(questions) - 1 else len(pretty_data)
        # Find the substring between the current question and the next one
        answer = pretty_data[pretty_data.find(
            question) + len(question):next_question_index]
        # Remove unwanted characters (":", ",") from the answer
        answer = answer.replace(":", "").replace(",", "").strip()
        # Store key-value pair in the dictionary
        extracted_data[question] = answer

    extracted_data['email'] = email
    return extracted_data


@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        # Access form fields from request.form
        form_id = request.form.get('formID')
        submission_id = request.form.get('submissionID')
        webhook_url = request.form.get('webhookURL')
        pretty_data = request.form.get('pretty')

        # Check if required fields are missing
        if not (form_id and submission_id and webhook_url and pretty_data):
            return 'One or more required fields are missing.', 400

        # Parse 'prettyData'
        parsed_data = parse_pretty_data(pretty_data)

        # Construct a document with the form data
        document = {
            'formID': form_id,
            'submissionID': submission_id,
            'webhookURL': webhook_url,
            **parsed_data  # Add parsed data to the document
        }

        # Insert document into MongoDB collection
        result = collection.insert_one(document)

        # Return a success response
        return jsonify({'message': 'Document inserted successfully', 'inserted_id': str(result.inserted_id)}), 200

    except Exception as e:
        # Return an error response if there's an exception
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
