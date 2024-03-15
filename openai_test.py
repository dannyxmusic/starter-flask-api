from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage, AIMessage
from bson import ObjectId
import json
import os
import re
import sys
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO

# Define the logger
logger = logging.getLogger(__name__)

# MongoDB Atlas connection URI
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)

# Access the database and collection
db = client['tpc_survey_f1']
collection = db['cyclic_server']
object_id_str = sys.argv[1]
object_id = ObjectId(object_id_str)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

llm = OpenAI(openai_api_key=OPENAI_API_KEY)


def process_openai(insert_id, data):
    # Convert insert_id to ObjectId
    try:
        insert_id = ObjectId(insert_id)
    except Exception as e:
        print(f"Error converting insert_id to ObjectId: {e}")
        sys.exit(1)

    data_from_db = collection.find_one({"_id": insert_id})

    if not data_from_db:
        print(f"Document with _id {insert_id} not found.")
        sys.exit(1)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("ai", "you are a helpful chatbot"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    prompt2 = ChatPromptTemplate.from_messages(
        [
            ("ai", "analyze the sentiment and return only a numerical value"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    memory = ConversationBufferMemory(return_messages=True)

    memory.load_memory_variables({})

    chain = (
        RunnablePassthrough.assign(
            history=RunnableLambda(
                memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | llm
    )

    chain2 = (
        RunnablePassthrough.assign(
            history=RunnableLambda(
                memory.load_memory_variables) | itemgetter("history")
        )
        | prompt2
        | llm
    )

    inputs = {"input": ("Please review this survey data: " f"{data}")}
    response = chain.invoke(inputs)

    memory.save_context(inputs, {"output": response})

    history = memory.load_memory_variables({})

    inputs = {
        "input": "Gauge the sentiment and normalize on a scale of 0-1.0. The response to (enter your email), (how many employees), and (please add additional feedback) are all user input. However all other survey questions are rated from very difficult to very easy, dissatisfied to very satisfied, and unlikely to very likely. Please refer to the survey responses and estimate a normalized sentiment value. Return the numerical value you've determined and no other context."}
    response = chain2.invoke(inputs)

    sentiment_temperature = response

    memory.save_context(inputs, {"output": response})

    memory.load_memory_variables({})

    inputs = {
        "input": "Write a testimonial from the perspective of the person who completed the survey. The testimonial should be 30-50 words long. Include the response from the final survey question (survey question containing = please provide any additional feedback) to retain authenticity of the review. /n If the sentiment is below a 0.5 try to write with gracious feedback and a positive outlook for the company."}
    response = chain.invoke(inputs)

    memory.save_context(inputs, {"output": response})

    memory.load_memory_variables({})

    inputs = {
        "input": "Write a testimonial from the perspective of the person who completed the survey. This testimonial should be 60-80 words long. Include the response from the final survey question (survey question containing = please provide any additional feedback) to retain authenticity of the review. /n If the sentiment is below a 0.5 try to write with gracious feedback and a positive outlook for the company."}
    response = chain.invoke(inputs)

    memory.save_context(inputs, {"output": response})

    memory.load_memory_variables({})

    inputs = {
        "input": "Write a testimonial from the perspective of the person who completed the survey. The testimonial should be 100 words or longer. Include the response from the final survey question (survey question containing = please provide any additional feedback) to retain authenticity of the review. /n If the sentiment is below a 0.5 try to write with gracious feedback and a positive outlook for the company."}
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

    # Fixing the issues in the data
    fixed_data = {}
    for key, value in conversation_history.items():
        # Remove leading and trailing whitespace
        value = value.strip()

        # Check if the key corresponds to content2, content4, content6, content8, or content10
        if key in ['content2', 'content4', 'content6', 'content8', 'content10']:
            # Remove any occurrences of 'AI:' followed by whitespace or newline characters
            value = re.sub(r'AI:\s*', '', value)
            # Insert 'AI: ' at the beginning
            value = 'AI: ' + value.strip()

        # Store the cleaned content and response as key-value pairs
        cleaned_history[content] = response

     # Print conversationHistory_json in the logger
    logger.info("Conversation history JSON:\n%s", cleaned_history)

    data = cleaned_history

    try:
        # Update the original document with conversation history
        collection.update_one({"_id": insert_id}, {
                              "$set": {"conversationHistory": data}})
        print(f"Conversation history updated for document with _id "
              f"{insert_id}")

    except Exception as e:
        print(f"Error updating conversation history: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python openai.py <insert_id> <data>")
        sys.exit(1)
    insert_id = sys.argv[1]
    data = json.loads(sys.argv[2])
    process_openai(insert_id, data)
