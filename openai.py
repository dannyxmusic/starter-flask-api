from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.messages import HumanMessage, AIMessage
import json
import os

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

llm = OpenAI(openai_api_key=OPENAI_API_KEY)
chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY,
                        model="gpt-3.5-turbo-0125")

prompt = ChatPromptTemplate.from_messages(
    [
        ("ai", "you are a helpful chatbot"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

prompt2 = ChatPromptTemplate.from_messages(
    [
        ("ai", "you analyze sentiment and return only a numerical value"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

data = {
    "id": "65f129dcdb2584c82ebeaebe",
    "formID": "232965699713170",
    "submissionID": "5860787365883384835",
    "webhookURL": "https://easy-plum-stingray-toga.cyclic.app/submit-form",
    "data": {
        "Please Enter your Email Address": "test@gmail.com",
        "How would you rate the ease of transitioning and implementation to TPC's services from your previous payroll provider?": "Easy",
        "TPC's HR and payroll software?": "Very Easy",
        "Who was your previous Payroll Provider?": "ADP",
        "How would you rate your satisfaction for TPC over your previous payroll provider?": "Very Satisfied",
        "How would you rate your experience with TPC's customer service in addressing your inquiries and concerns?": "Neutral",
        "How many employees does your company currently process payroll for?": "23",
        "How inclined are you to recommend Grant Stuart and TPC's services to another business?": "Somewhat Likely",
        "Please share your experience or any additional feedback you have regarding your experience with Grant Stuart and TPC.": "Great service, Great Company! I will definitely recommend them to my friends who own businesses."
    }
}


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
    "input": "Gauge the sentiment and normalize. The response to (enter your email), (how many employees), and (please add additional feedback) are all user input. However all other survey questions are rated from very difficult to very easy, dissatisfied to very satisfied, and unlikely to very likely. Please refer to the survey responses and estimate a normalized sentiment value. Return the numerical value you've determined and no other context."}
response = chain2.invoke(inputs)

sentiment_temperature = response

memory.save_context(inputs, {"output": response})

memory.load_memory_variables({})

inputs = {
    "input": "Write a testimonial from the perspective of the person who completed the survey. The testimonial should be 30-50 words long. Include the wording from the final survey question (please provide any additional feedback) to retain authenticity of the review."}
response = chain.invoke(inputs)

memory.save_context(inputs, {"output": response})

memory.load_memory_variables({})

inputs = {
    "input": "Write a testimonial from the perspective of the person who completed the survey. This testimonial should be 60-80 words long. Include the wording from the final survey question (please provide any additional feedback) to retain authenticity of the review."}
response = chain.invoke(inputs)

memory.save_context(inputs, {"output": response})

memory.load_memory_variables({})

inputs = {
    "input": "Write a testimonial from the perspective of the person who completed the survey. The testimonial should be 100 words or longer. Include the wording from the final survey question (please provide any additional feedback) to retain authenticity of the review. Be professional and detailed."}
response = chain.invoke(inputs)

memory.save_context(inputs, {"output": response})
history = memory.load_memory_variables({})

conversationHistory = []

# Extract content from each message in the history and add it to conversationHistory
for i, message in enumerate(history['history'], start=1):
    content_key = f"content{i}"
    if isinstance(message, HumanMessage):
        content = message.content
        conversationHistory.append({content_key: content})
    elif isinstance(message, AIMessage):
        content = message.content
        conversationHistory.append({content_key: content})


conversationHistory_json = json.dumps(conversationHistory, indent=2)


print(conversationHistory_json)
