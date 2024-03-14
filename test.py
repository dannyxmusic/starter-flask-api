import sys
import os
import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MongoDB Atlas connection URI
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)


def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python test.py <insert_id>")
        sys.exit(1)

    insert_id = sys.argv[1]
    logger.info(f"Insert ID received as command-line argument: {insert_id}")

    # Access the database and collection
    db = client['tpc_survey_f1']
    collection = db['cyclic_server']

    logger.info("Attempting to find document in MongoDB collection...")
    document = collection.find_one({"_id": insert_id})
    if document:
        logger.info("Document found:")
        logger.info(document)
    else:
        logger.error(f"No document found with _id: {insert_id}")


if __name__ == "__main__":
    main()
