import json
import os
import base64
import sys
from email.message import EmailMessage
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pymongo import MongoClient
from bson import ObjectId

# Gmail credentials
GMAIL_REFRESH_TOKEN = os.environ.get('GMAIL_REFRESH_TOKEN')
GMAIL_CLIENT_ID = os.environ.get('GMAIL_CLIENT_ID')
GMAIL_CLIENT_SECRET = os.environ.get('GMAIL_CLIENT_SECRET')

# Prepare the request payload
payload = {
    "client_id": GMAIL_CLIENT_ID,
    "client_secret": GMAIL_CLIENT_SECRET,
    "refresh_token": GMAIL_REFRESH_TOKEN,
    "grant_type": "refresh_token"
}

# Send a POST request to obtain a new access token
response = requests.post(
    "https://www.googleapis.com/oauth2/v4/token", data=payload)

# Check the response status code
if response.status_code == 200:
    # Parse the JSON response
    token_data = response.json()

    # Extract the new access token
    access_token = token_data.get("access_token")

    # MongoDB URI
    MONGO_URI = os.environ.get('MONGO_URI')

    # Initialize OAuth 2.0 credentials
    credentials = Credentials(
        token=access_token,
        refresh_token=GMAIL_REFRESH_TOKEN,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=GMAIL_CLIENT_ID,
        client_secret=GMAIL_CLIENT_SECRET
    )

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=credentials)

    # MongoDB client
    client = MongoClient(MONGO_URI)
    db = client['tpc_survey_f1']
    collection = db['cyclic_server']
    collection2 = db['survey1_testimonials']

    # Extract content function
    def extract_content(doc):
        """
        Extracts email address and testimonial content from document.

        Args:
            doc (dict): The document from MongoDB.

        Returns:
            tuple: Email address and testimonial content.
        """
        conversation_history = doc.get('survey_responses', {})
        email_address = doc.get('email', '')
        content_keys = ["content8", "content10", "content12"]
        content_values = [conversation_history.get(
            key, '') for key in content_keys]
        return email_address, content_values

    object_id = sys.argv[1]
    object_id = ObjectId(object_id)

    survey_responses_str = sys.argv[5]
    survey_responses = json.loads(survey_responses_str)

    formatted_survey_responses = ""
    for question, answer in survey_responses.items():
        formatted_survey_responses += f"{question}: {answer}\n\n"

    short_testimonial = sys.argv[2]
    medium_testimonial = sys.argv[3]
    long_testimonial = sys.argv[4]

    document = collection.find_one({"_id": object_id})

    email_address, content = extract_content(document)

    first_item = short_testimonial
    second_item = medium_testimonial
    third_item = long_testimonial

    message_body = (
        f"Email: {email_address}\n \n"
        f"Short Testimonial: {first_item}\n \n"
        f"Medium Testimonial: {second_item}\n \n"
        f"Long Testimonial: {third_item}\n \n"
        f"Survey Responses:\n{formatted_survey_responses}"
    )

    message = EmailMessage()
    message.set_content(message_body)
    message["To"] = "sandagedaniel@gmail.com, "  "grant@thepayrollco.com"
    message["From"] = "therealdannyx@gmail.com"
    message["Subject"] = "New Ai Testimonial"

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        send_message = (
            service.users().messages()
            .send(userId="me", body={"raw": encoded_message})
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except Exception as error:
        print(f"An error occurred: {error}")

else:
    print("Failed to refresh access token. Status code:", response.status_code)
