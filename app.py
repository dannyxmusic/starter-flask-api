from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# MongoDB API key fetched from environment variables
mongodb_api_key = os.environ.get('MONGODB_API_KEY')
mongodb_api_url = os.environ.get('MONGODB_API_URL')


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

        # Construct a dictionary with the form data
        data = {
            'formID': form_id,
            'submissionID': submission_id,
            'webhookURL': webhook_url,
        }

        # Parse 'prettyData'
        parsed_data = parse_pretty_data(pretty_data)

        # Update 'data' dictionary with parsed data
        data.update(parsed_data)

        print(f"{mongodb_api_url}/insertOne", "api-key =" f"{mongodb_api_key}")

        # Make API request to MongoDB Atlas API
        response = requests.post(
            f"{mongodb_api_url}/insertOne",
            json={
                "dataSource": "testimonialGenerator",
                "database": "tpc_survey_f1",
                "collection": "cyclic_server",
                "document": data
            },
            headers={"Content-Type": "application/json",
                     "api-key": mongodb_api_key
                     }
        )

        # Simulate a successful response
        return jsonify(response.json()), 200

    except Exception as e:
        # Return an error response if there's an exception
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
