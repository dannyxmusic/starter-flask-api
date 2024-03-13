from flask import Flask, request, jsonify

app = Flask(__name__)


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

    # Iterate through each question
    for i in range(len(questions)):
        question = questions[i]
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

    return extracted_data


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

        # Parse 'prettyData'
        parsed_data = parse_pretty_data(pretty_data)

        # Update 'data' dictionary with parsed data
        data['parsedData'] = parsed_data

        # Print the JSON data
        print(data)

        # Return a success response
        return data

    except Exception as e:
        # Log the error
        print('An error occurred:', e)
        # Return an error response
        return 'An error occurred while processing the data.', 500


if __name__ == '__main__':
    app.run(debug=True)
