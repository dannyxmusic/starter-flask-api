import json
import re

# Read the contents of the JSON file
with open('payload.json', 'r') as file:
    json_string = file.read()

# Parse the JSON string into a Python dictionary
data = json.loads(json_string)

# Extract specific fields
form_id = data.get('formID', None)
submission_id = data.get('submissionID', None)
webhook_url = data.get('webhookURL', None)
pretty_info = data.get('pretty', None)

# Define a regular expression pattern to match each question-response pair
pattern = r'([^:,]+):([^:,]+)'

# Extract question-response pairs using the regular expression
pairs = re.findall(pattern, pretty_info)

# Initialize an empty dictionary to store the question-response pairs
parsed_data = {}

# Iterate through the pairs
for pair in pairs:
    # Remove any leading/trailing whitespace from the question and response
    question = pair[0].strip()
    response = pair[1].strip()
    # Add the question-response pair to the dictionary
    parsed_data[question] = response

# Add formID, submissionID, and webhookURL to the parsed data
parsed_data['formID'] = form_id
parsed_data['submissionID'] = submission_id
parsed_data['webhookURL'] = webhook_url

# Convert the dictionary to JSON format
json_data = json.dumps(parsed_data, indent=4)

# Print the JSON data
print(json_data)
