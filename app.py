import json
import logging
import os
import subprocess

from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Atlas connection URI
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)

# Access the database and collection
db = client['tpc_survey_f1']
collection = db['cyclic_server']

# Path to the openai.py script
OPENAI_SCRIPT_PATH = 'openai_tg_copy.py'


def parse_pretty_data(pretty_data):
    """
    Parse the pretty data received from the form submission.

    Args:
        pretty_data (str): The pretty-formatted data received from the form.

    Returns:
        dict: A dictionary containing the parsed data.
    """
    questions = [
        "Please Enter your Email Address",
        "How would you rate the ease of transitioning and implementation to TPC's services from your previous payroll provider?",
        "How user-friendly do you find iSolved, TPC's HR and payroll software?",
        "Who was your previous Payroll Provider?",
        "What field or industry does your company specialize in?"
        "How would you rate your satisfaction for TPC over your previous payroll provider?",
        "How would you rate your experience with TPC's customer service in addressing your inquiries and concerns?",
        "How many employees does your company currently process payroll for?",
        "How inclined are you to recommend Grant Stuart and TPC's services to another business?",
        "Please share your experience or any additional feedback you have regarding your experience with Grant Stuart and TPC."
    ]

    extracted_data = {}
    survey_responses = {}

    for i, question in enumerate(questions):
        if "Please Enter your Email Address" in question:
            email = pretty_data.split(":")[1].strip().split(",")[0]
            continue

        next_question_index = pretty_data.find(
            questions[i + 1]) if i < len(questions) - 1 else len(pretty_data)
        answer = pretty_data[pretty_data.find(
            question) + len(question):next_question_index]
        answer = answer.replace(":", "").replace(",", "").strip()

        # Exclude email from survey responses
        if "Please Enter your Email Address" not in question:
            survey_responses[question] = answer

    extracted_data['email'] = email
    extracted_data['survey_responses'] = survey_responses

    return extracted_data


@app.route('/submit-form', methods=['POST'])
def submit_form():
    """
    Endpoint to handle form submissions.
    """
    try:
        form_id = request.form.get('formID')
        submission_id = request.form.get('submissionID')
        webhook_url = request.form.get('webhookURL')
        pretty_data = request.form.get('pretty')

        if not all([form_id, submission_id, webhook_url, pretty_data]):
            return 'One or more required fields are missing.', 400

        parsed_data = parse_pretty_data(pretty_data)

        document = {
            'formID': form_id,
            'submissionID': submission_id,
            'webhookURL': webhook_url,
            **parsed_data
        }

        result = collection.insert_one(document)

        # Pass parsed_data to openai.py
        test_process = subprocess.Popen(['python', OPENAI_SCRIPT_PATH, str(result.inserted_id)],
                                        stdout=subprocess.PIPE)
        test_output, _ = test_process.communicate()
        test_output = test_output.decode('utf-8').strip()

        return jsonify({
            'message': 'Document inserted successfully',
            'inserted_id': str(result.inserted_id),
        }), 200

    except KeyError as e:
        logger.error(f'Missing field: {str(e)}')
        return jsonify({'error': f'Missing field: {str(e)}'}), 400

    except Exception as e:
        logger.exception(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
