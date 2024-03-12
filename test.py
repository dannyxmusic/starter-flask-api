import json
import re


def process_payload(json_string):
    # Parse the JSON string into a Python dictionary
    data = json.loads(json_string)

    # Extract specific fields
    form_id = data.get('formID', None)
    submission_id = data.get('submissionID', None)
    webhook_url = data.get('webhookURL', None)
    pretty_info = data.get('pretty', None)

    # Define a regular expression pattern to match each question-response pair
    pattern = r'([^:,]+:[^:,]+)'

    # Extract question-response pairs using the regular expression
    pairs = re.findall(pattern, pretty_info)

    # Initialize an empty dictionary to store the question-response pairs
    parsed_data = {}

    # Iterate through the pairs and split them by ':'
    for pair in pairs:
        # Split the pair by ':'
        question, response = pair.split(':', 1)
        # Remove any leading/trailing whitespace from the question and response
        question = question.strip()
        response = response.strip()
        # Add the question-response pair to the dictionary
        parsed_data[question] = response

    # Return the parsed data as JSON
    return parsed_data
