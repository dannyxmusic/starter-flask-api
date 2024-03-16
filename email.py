from googleapiclient.errors import HttpError
from email.message import EmailMessage
from pymongo import MongoClient
from bson import ObjectId
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
import sys
import os

GMAIL_ACCESS_TOKEN = os.environ.get('GMAIL_ACCESS_TOKEN')
GMAIL_REFRESH_TOKEN = os.environ.get('GMAIL_REFRESH_TOKEN')
GMAIL_CLIENT_ID = os.environ.get('GMAIL_CLIENT_ID')
GMAIL_CLIENT_SECRET = os.environ.get('GMAIL_CLIENT_SECRET')
MONGO_URI = os.environ.get('MONGO_URI')

# Set up OAuth 2.0 credentials
credentials = Credentials(
    GMAIL_ACCESS_TOKEN,
    refresh_token=GMAIL_REFRESH_TOKEN,
    token_uri='https://oauth2.googleapis.com/token',
    client_id=GMAIL_CLIENT_ID,
    client_secret=GMAIL_CLIENT_SECRET
)

# Build the Gmail service
service = build('gmail', 'v1', credentials=credentials)

client = MongoClient(MONGO_URI)

# Access the database and collection
db = client['tpc_survey_f1']
collection = db['cyclic_server']
collection2 = db['survey1_testimonials']
object_id_str = sys.argv[1]
objectId = ObjectId(object_id_str)


def extract_content(doc):
    conversation_history = doc.get('conversationHistory', {})
    return [conversation_history.get(key, '') for key in ["content8", "content10", "content12"]]


# Find document with the current random ID
document = collection.find_one({"_id": objectId})
# Extract the content from the document
content = extract_content(document)

first_item = content[0]
second_item = content[1]
third_item = content[2]

message = (
    f"Short Testimonial: {first_item}\n \n"
    f"Medium Testimonial: {second_item}\n \n"
    f"Long Testimonial: {third_item}"
)


def send_email(service, data):
    try:
        # Construct the email message
        message = EmailMessage()
        message.set_content(str(data))
        message["To"] = "sandagedaniel@gmail.com"
        message["From"] = "therealdannyx@gmail.com"
        message["Subject"] = "test"

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        send_message = (
            service.users().messages()
            .send(userId="me", body={"raw": encoded_message})
            .execute()
        )

        print(f'Message Id: {send_message["id"]}')
        return send_message

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


send_email(service, message)
