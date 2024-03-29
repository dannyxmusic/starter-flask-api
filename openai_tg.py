import asyncio
import logging
import os
import subprocess
import sys
import random
import aiohttp  # Added import statement

from operator import itemgetter
from bson import ObjectId
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient
import requests

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

# Initialize OpenAI instance
model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.2,
                   api_key=OPENAI_API_KEY)
model2 = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.8,
                    api_key=OPENAI_API_KEY)

# Initialize output parser
output_parser = StrOutputParser()


async def send_post_request(summary, history, insert_id):
    """
    Send HTTP POST request with summary and history data.
    """
    logger = logging.getLogger(__name__)
    try:
        url = 'https://easy-plum-stingray-toga.cyclic.app/process_openai2'
        async with aiohttp.ClientSession() as session:
            payload = {
                'summary': summary,
                'history': history,
                'insert_id': insert_id
            }
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(
                        'Internal HTTP request to process_openai endpoint successful')
                else:
                    logger.error(
                        'Internal HTTP request to process_openai endpoint failed')
    except Exception as e:
        logger.error(f'An error occurred: {str(e)}')


async def process_openai(insert_id, survey_data):
    """
    Process data using OpenAI.
    """
    survey_responses = survey_data

    all_ids = [doc["_id"] for doc in collection2.find({}, {"_id": 1})]
    random_ids = random.sample(all_ids, 2)
    logger.info(f"Randomly selected IDs: {random_ids}")

    def extract_content(doc):
        return ' '.join([doc[key] for key in ["short_testimonial", "medium_testimonial", "long_testimonial"]])

    contents = []

    for random_id in random_ids:
        document = collection2.find_one({"_id": random_id})
        content = extract_content(document)
        contents.append(content)

    prompt1 = ChatPromptTemplate.from_messages([
        ("system", "You are an AI designed to assist in testimonial generation. I provide you survey results and you do 2 things; 1. analyze sentiment. 2. Detect recurring wordage or phrasing from previous testimonials."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    prompt2 = ChatPromptTemplate.from_messages([
        ("system", "You are an AI tool designed to assist in testimonial generation. I provide you survey results and you do 3 things; 1. List all the survey responses from the original object id #. 2. extract any recurring wordage or phrasing from previous testimonials or listed by ai in the conversation history. 3. Briefly summarize the conversation between human and AI for contextual prompt generation."),
        ("human", "{input}"),
    ])

    memory = ConversationBufferMemory(return_messages=True)
    memory.load_memory_variables({})

    chain = (RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
        | prompt1 | model | output_parser)

    chain2 = prompt2 | model | output_parser

    inputs = {"input": "What is your purpose?"}
    response = chain.invoke(inputs)

    memory.save_context(inputs, {"output": response})

    memory.load_memory_variables({})

    inputs = {
        "input": f"Here is a survey with the '_id': {insert_id}. Please review the survey and confirm that you processed the data: Survey response = {survey_responses}"
    }

    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    inputs = {
        "input": f"Before I ask you to generate a testimonial I'd like you to review these historical testimonial responses for recurring language. Document them and we will avoid using repeat language in our future testimonial generations. Historical Documents = {contents}"
    }
    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    history = memory.load_memory_variables({})

    inputs = {
        "input": f"Please review the conversation history. conversation_history = {history}"
    }
    summary = chain2.invoke(inputs)

    # Asynchronously process the openai.py script
    asyncio.create_task(send_post_request(summary, history, insert_id))

    logger.info('Task Created')

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.error("Usage: python openai_test.py <insert_id> <data>")
        sys.exit(1)

    insert_id = sys.argv[1]
    survey_data = sys.argv[2]
    logger.info(f'Insert Id: {insert_id}')

    # Run process_openai asynchronously
    asyncio.run(process_openai(insert_id=insert_id, survey_data=survey_data))

    # Close MongoDB connection
    client.close()
