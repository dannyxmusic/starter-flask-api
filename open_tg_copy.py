import argparse
from operator import itemgetter
import random
import subprocess
import os
from bson import ObjectId
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient

# Initialize MongoDB client
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['tpc_survey_f1']
collection = db['cyclic_server']
collection2 = db['survey1_testimonials']

# Path to the email.py script
EMAIL_SCRIPT_PATH = 'email_tg.py'

# Initialize OpenAI model
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.2,
                   api_key=OPENAI_API_KEY)
model2 = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.8,
                    api_key=OPENAI_API_KEY)

# Initialize conversation memory
memory = ConversationBufferMemory(return_messages=True)
memory.load_memory_variables({})

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
        serialized_history = [{'type': 'human', 'content': message.content} if isinstance(message, HumanMessage)
                              else {'type': 'ai', 'content': message.content} for message in context['history']]

        filtered_response = {
            "submission_id": submission_id,
            "context": serialized_history,
            "summary": summary,
            "short_testimonial": short,
            "medium_testimonial": medium,
            "long_testimonial": long,
        }

        # Insert the document into MongoDB collection
        collection2.insert_one(filtered_response)

        print("Testimonials updated successfully.")
    except Exception as e:
        print(f"Error occurred while updating testimonials: {e}")
        # Handle the error appropriately (e.g., log the error, return an error message)


def generate_testimonials(insert_id):
    """
    Generate testimonials based on survey responses.

    Args:
        insert_id (str): The ID of the document.
        data (dict): The data to process.
    """
    objectId = ObjectId(insert_id)
    data_from_db = collection.find_one({"_id": objectId})

    # Extract survey responses
    survey_responses = data_from_db['survey_responses']
    submission_id = data_from_db['submissionID']
    amt_employees = survey_responses["How many employees does your company currently process payroll for?"]
    additional_feedback = survey_responses["Please share your experience or any additional feedback you have regarding your experience with Grant Stuart and TPC."]
    prev_provider = survey_responses["Who was your previous Payroll Provider?"]

    # Run OpenAI models
    prompt1 = ChatPromptTemplate.from_messages([
        ("system", "You are an AI designed to assist in testimonial generation. I provide you survey results and you do 2 things; 1. analyze sentiment. 2. Detect recurring wordage or phrasing from previous testimonials."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    prompt2 = ChatPromptTemplate.from_messages([
        ("system", "You are an AI tool designed to assist in testimonial generation. I provide you survey results and you do 3 things; 1. List all the survey responses from the original object id #. 2. extract any recurring wordage or phrasing from previous testimonials or listed by ai in the conversation history. 3. Briefly summarize the conversation between human and AI for contextual prompt generation."),
        ("human", "{input}"),
    ])

    prompt3 = ChatPromptTemplate.from_messages([
        ("system", "You are an AI tool designed generate a testimonial based on survey results. You do 3 things. Write in first person from the perspective of the customer. 2. Avoid using the provided recurring words and phrases and find alternatives. 3. Generate a unique testimonials"),
        ("human", "{input}"),
    ])

    chain = (RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
        | prompt1 | model | output_parser)

    chain2 = prompt2 | model | output_parser

    chain3 = (prompt3 | model2 | output_parser)

    # Generate testimonials
    inputs = {"input": f"Here is a survey with the '_id': {objectId}. Please review the survey and confirm that you processed the data: Survey response = {survey_responses}"}

    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    # Retrieve all "_id" values from the collection
    all_ids = [doc["_id"] for doc in collection2.find({}, {"_id": 1})]

    # Randomly select two "_id" values from the list
    random_ids = random.sample(all_ids, 2)

    def extract_content(doc):
        return ' '.join([doc[key] for key in ["short_testimonial", "medium_testimonial", "long_testimonial"]])

    contents = []

    # Iterate over the randomly selected IDs
    for random_id in random_ids:
        # Find document with the current random ID
        document = collection2.find_one({"_id": random_id})
        # Extract the content from the document
        content = extract_content(document)
        # Append the content to the list
        contents.append(content)

    inputs = {"input": f"Before I ask you to generate a testimonial I'd 
              like you to review these historical testimonial responses for recurring language. Document them and we will avoid using repeat language in our future testimonial generations. Historical Documents = {contents}"}
    response = chain.invoke(inputs)
    memory.save_context(inputs, {"output": response})

    history = memory.load_memory_variables({})

    inputs = {
        "input": f"Please review the conversation history. conversation_history = {history}"}
    summary = chain2.invoke(inputs)

    input1 = {'input': f'Review the context: context={summary}. \nGenerate 
              a 60-80 word testimonial using the information provided. Incorporate the amount of employees the company has ({amt_employees}). If the previous payroll provider is listed then mention the company ({prev_provider}). If the additional feedback ({additional_feedback}) is negative please reword to have a positive outlook for future improvements. If the additional feedback ({additional_feedback}) is positive please incorporate verbatim the customer\'s wording to retain authenticity of the testimony.'}
    
    medium_testimony = chain3.invoke(input1)

    input2 = {'input': f'Review the context: context={summary}. \nGenerate 
              a short 30-50 word testimonial using the information provided. Incorporate the amount of employees the company has ({amt_employees}). If the previous payroll provider is listed then mention the company ({prev_provider}). If the additional feedback ({additional_feedback}) is negative please reword to have a positive outlook for future improvements. If the additional feedback ({additional_feedback}) is positive please incorporate verbatim the customer\'s wording to retain authenticity of the testimony.'}
    
    short_testimony = chain3.invoke(input2)

    input3 = {'input': f'Review the context: context={summary}. \nGenerate 
              a long 100-120 word testimonial using the information provided. Incorporate the amount of employees the company has ({amt_employees}). If the previous payroll provider is listed then mention the company ({prev_provider}). If the additional feedback ({additional_feedback}) is negative please reword to have a positive outlook for future improvements. If the additional feedback ({additional_feedback}) is positive please incorporate verbatim the customer\'s wording to retain authenticity of the testimony.'}
    
    long_testimony = chain3.invoke(input3)

    append_testimonials(context=history, summary=summary, short=short_testimony,
                        medium=medium_testimony, long=long_testimony, submission_id=submission_id)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process survey data and generate testimonials")
    parser.add_argument("insert_id", type=str, help="The ID of the document")
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    insert_id = args.insert_id
    objectId = ObjectId(insert_id)

    generate_testimonials(objectId)

    # Call the email.py script
    subprocess.run(['python', EMAIL_SCRIPT_PATH, insert_id])


if __name__ == "__main__":
    main()
