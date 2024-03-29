import asyncio
import json
import logging
import os
import subprocess
import sys

from bson import ObjectId
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Atlas connection URI
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)

# Access the database and collection
db = client['tpc_survey_f1']
collection = db['cyclic_server']
collection2 = db['survey1_testimonials']


# Path to the email.py script
EMAIL_SCRIPT_PATH = 'email_tg.py'

# Path to the OpenAI API key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

model2 = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7,
                    api_key=OPENAI_API_KEY)

# Initialize output parser
output_parser = StrOutputParser()


def append_testimonials(context, summary, short, medium, long, submission_id):
    """
    Update testimonials in MongoDB collection.

    Args:
        context (dict): The context containing conversation history.
        summary (str): Summary of the testimonials.
        short (str): Short testimonial.
        medium (str): Medium-length testimonial.
        long (str): Long testimonial.
        submission_id (str): The submission ID associated with the testimonials.
    """
    try:
        filtered_response = {
            "submission_id": submission_id,
            "context": context,
            "summary": summary,
            "short_testimonial": short,
            "medium_testimonial": medium,
            "long_testimonial": long,
        }
        collection2.insert_one(filtered_response)
        print("Testimonials updated successfully.")
    except Exception as e:
        print(f"Error occurred while updating testimonials: {e}")


async def process_openai(summary, history, insert_id):
    """
    Process data using OpenAI.

    Args:
        insert_id (str): The ID of the document.
        data (dict): The data to process.
    """
    logger.info('Generating Testimonials...')
    insert_id = ObjectId(insert_id)
    key1 = "Please share your experience or any additional feedback you have regarding your experience with Grant Stuart and TPC."
    key3 = "How many employees does your company currently process payroll for?"
    key4 = "Who was your previous Payroll Provider?"

    data = collection.find_one({"_id": insert_id})
    submission_id = data['submissionID']
    survey_responses = data['survey_responses']
    amt_employees = survey_responses[key3]
    additional_feedback = survey_responses[key1]
    prev_provider = survey_responses[key4]

    prompt3 = ChatPromptTemplate.from_messages([
        ("system", "You are an AI tool designed generate a testimonial based on survey results. You do 3 things. 1. Recieve a summary which includes the survey responses, words/phrases to omit, and context. 2. Write in first person from the client who completed the survey. 3. Generate a uniquely worded testimonials.'"),
        ("human", "{input}"),
    ])

    chain3 = (prompt3 | model2 | output_parser)

    input1 = {
        'input': f'Review the data: summary={summary}. Do not use words or phrases listed in section 2 of the summary. \nGenerate a 60-80 word testimonial using the information provided. Include the amount of employees the company has ({amt_employees}). Mention the company ({prev_provider}). Include some of this ({additional_feedback}) if it has a positive sentiment. Do not start the testimonial with "Transitioning to TPC", "transitioning", "The transition", or "I recently transitioned".'
    }

    medium_testimony = chain3.invoke(input1)
    # logger.info(medium_testimony)

    input2 = {
        'input': f'Review the context: context={summary}. Do not use words or phrases listed in section 2 of the context. \nGenerate a 30-50 word testimonial using the information provided. Include the amount of employees the company has ({amt_employees}). Mention the company ({prev_provider}). Include some of this ({additional_feedback}) if it has a positive sentiment. Do not start the testimonial with "Transitioning to TPC", "transitioning", "The transition", or "I recently transitioned".'
    }

    short_testimony = chain3.invoke(input2)
    # logger.info(short_testimony)

    input3 = {
        'input': f'Review the context: context={summary}. Do not use words or phrases listed in section 2 of the context. \nGenerate a 100-120 word testimonial using the information provided. Include the amount of employees the company has ({amt_employees}). Mention the company ({prev_provider}). Include some of this ({additional_feedback}) if it has a positive sentiment. Do not start the testimonial with "Transitioning to TPC", "transitioning", "The transition", or "I recently transitioned".'
    }

    long_testimony = chain3.invoke(input3)
    # logger.info(long_testimony)

    # Convert survey_responses to a string
    survey_responses_str = json.dumps(survey_responses)

    # Update the original document with conversation history
    append_testimonials(
        context=history, summary=summary, short=short_testimony,
        medium=medium_testimony, long=long_testimony, submission_id=submission_id
    )

    print(type(insert_id), type(short_testimony), type(
        medium_testimony), type(long_testimony), type(survey_responses_str)
    )

    # Call the email.py script
    subprocess.run(
        ['python', EMAIL_SCRIPT_PATH, str(insert_id), short_testimony,
         medium_testimony, long_testimony, survey_responses_str]
    )


async def main(summary, history, insert_id):
    """
    Main entry point of the script.
    """
    # Run process_openai asynchronously
    await process_openai(summary, history, insert_id)
    print('Testimonials generated')


if __name__ == "__main__":
    if len(sys.argv) < 4:
        logger.error("Usage: python openai_test.py <insert_id> <data>")
        sys.exit(1)

    summary = sys.argv[1]
    history = sys.argv[2]
    insert_id = sys.argv[3]

    # Run the main function asynchronously
    asyncio.run(main(summary, history, insert_id))
