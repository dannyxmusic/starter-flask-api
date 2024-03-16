import json
import logging
import os
import re
import subprocess
import sys
import random

from operator import itemgetter
from bson import ObjectId
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage, AIMessage
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

# Initialize OpenAI instance
llm = OpenAI(openai_api_key=OPENAI_API_KEY)


def process_openai(insert_id, data):
    """
    Process data using OpenAI.

    Args:
        insert_id (str): The ID of the document.
        data (dict): The data to process.
    """
    try:
        # Convert insert_id to ObjectId
        insert_id = ObjectId(insert_id)
    except Exception as e:
        logger.error(f"Error converting insert_id to ObjectId: {e}")
        sys.exit(1)

    data_from_db = collection.find_one({"_id": insert_id})

    if not data_from_db:
        logger.error(f"Document with _id {insert_id} not found.")
        sys.exit(1)

    # Retrieve all "_id" values from the collection
    all_ids = [doc["_id"] for doc in collection2.find({}, {"_id": 1})]

    # Randomly select two "_id" values from the list
    random_ids = random.sample(all_ids, 2)
    logger.info(f"Randomly selected IDs: {random_ids}")

    def extract_content(doc):
        return ' '.join([doc[key] for key in ["content8", "content10", "content12"]])

    contents = []

    # Iterate over the randomly selected IDs
    for random_id in random_ids:
        # Find document with the current random ID
        document = collection2.find_one({"_id": random_id})
        # Extract the content from the document
        content = extract_content(document)
        # Append the content to the list
        contents.append(content)

    prompt = ChatPromptTemplate.from_messages(
        [("ai", "you are a helpful chatbot"),
         MessagesPlaceholder(variable_name="history"),
         ("human", "{input}")]
    )

    prompt2 = ChatPromptTemplate.from_messages(
        [("ai", "analyze the sentiment and return only a numerical value"),
         MessagesPlaceholder(variable_name="history"),
         ("human", "{input}")]
    )

    memory = ConversationBufferMemory(return_messages=True)
    memory.load_memory_variables({})

    chain = (RunnablePassthrough.assign(
        history=RunnableLambda(
            memory.load_memory_variables) | itemgetter("history")) | prompt | llm)

    chain2 = (RunnablePassthrough.assign(
        history=RunnableLambda(
            memory.load_memory_variables) | itemgetter("history")) | prompt2 | llm)

    inputs = {"input": ("Please review this survey data: " f"{data}")}
    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    inputs = {"input": "Gauge the sentiment and normalize on a scale of 0-1.0. "
              "The response to (enter your email), (how many employees), "
              "and (please add additional feedback) are all user input. "
              "However all other survey questions are rated from very difficult "
              "to very easy, dissatisfied to very satisfied, and unlikely to very "
              "likely. Please refer to the survey responses and estimate a normalized "
              "sentiment value. Return the numerical value you've determined and no other context."}
    response = chain2.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    inputs = {"input": "Review previous testimonials, notate recurring phrases or language. "
              "Previous testimonies" f"{contents}"}
    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    inputs = {"input": "Write a testimonial from the perspective of the person who completed the survey. "
              "The testimonial should be 30-50 words long. Do not state that you recently "
              "completed a survey. Avoid using phrasing from the recurring phrases review. "
              "Each testimony should be unique while portraying the correct sentiment."}
    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    inputs = {"input": "Write a testimonial from the perspective of the person who completed the survey. "
              "This testimonial should be 60-80 words long. Do not state that you recently "
              "completed a survey. Avoid using phrasing from the recurring phrases review. "
              "Each testimony should be unique while portraying the correct sentiment."}
    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    inputs = {"input": "Write a testimonial from the perspective of the person who completed the survey. "
              "The testimonial should be 100 words or longer. Do not state that you recently "
              "completed a survey. Avoid using phrasing from the recurring phrases review. "
              "Each testimony should be unique while portraying the correct sentiment."}
    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    history = memory.load_memory_variables({})
    conversationHistory = []

    for i, message in enumerate(history['history'], start=1):
        content_key = f"content{i}"
        if isinstance(message, HumanMessage):
            content = message.content
            conversationHistory.append({content_key: f"Human: {content}"})
        elif isinstance(message, AIMessage):
            content = message.content
            conversationHistory.append({content_key: f"{content}"})

    conversationHistory_json = json.dumps(conversationHistory, indent=2)
    conversation_history = json.loads(conversationHistory_json)
    cleaned_history = {}

    # Iterate over each item in the conversation history
    for item in conversation_history:
        key = next(iter(item))  # Get the key of the dictionary
        # Get the value and remove leading/trailing whitespace
        value = item[key].strip()

        # Check if the key corresponds to content2, content4, content6, content8, or content10
        if key in ['content2', 'content4', 'content6', 'content8', 'content10']:
            # Remove any occurrences of 'AI:' followed by whitespace or newline characters
            value = re.sub(r'AI:\s*', '', value)
            # Insert 'AI: ' at the beginning
            value = 'AI: ' + value.strip()

        cleaned_history[key] = value

    try:
        # Update the original document with conversation history
        collection.update_one({"_id": insert_id}, {
                              "$set": {"conversationHistory": cleaned_history}})
    except Exception as e:
        logger.error(f"Error updating conversation history: {e}")


def update_testimonials(insert_id):
    """
    Update testimonials.

    Args:
        insert_id (str): The ID of the document.
    """
    # Convert insert_id to ObjectId
    insert_id = ObjectId(insert_id)

    result = collection.find_one({"_id": insert_id})

    filtered_response = {
        "content8": result.get("conversationHistory", {}).get("content8"),
        "content10": result.get("conversationHistory", {}).get("content10"),
        "content12": result.get("conversationHistory", {}).get("content12"),
        "submissionID": result.get("submissionID")
    }
    result = collection2.insert_one(filtered_response)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.error("Usage: python openai_test.py <insert_id> <data>")
        sys.exit(1)
    insert_id = sys.argv[1]
    objectId = ObjectId(insert_id)
    data = json.loads(sys.argv[2])
    process_openai(insert_id, data)
    update_testimonials(insert_id)
    # Call the email.py script
    subprocess.run(['python', EMAIL_SCRIPT_PATH, insert_id])
