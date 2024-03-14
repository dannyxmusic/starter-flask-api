import pymongo
import os
from flask import Flask

app = Flask(__name__)

# MongoDB connection URI
MONGO_URI = os.environ.get(
    "mongodb+srv://therealdannyx:dHMU3gO9o2vOrcPZ@testimonialgenerator.uz0hyl6.mongodb.net/?retryWrites=true&w=majority&appName=testimonialGenerator")

# Create a MongoClient instance
client = pymongo.MongoClient(MONGO_URI)

# Access a specific database
db = client['tpc_survey_f1']

# Access a specific collection
collection = db['cyclic_server']

# Define a route to check MongoDB connection and print documents


@app.route('/')
def index():
    try:
        # Check if connected to MongoDB
        if client.server_info():
            print('Connected to MongoDB and server is running')
            # Retrieve all documents from the collection
            cursor = collection.find({})
            for doc in cursor:
                print(doc)
            return 'Documents printed in console'
    except pymongo.errors.ServerSelectionTimeoutError as e:
        return f'Failed to connect to MongoDB: {e}', 500


# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)
