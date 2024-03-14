import sys
import os
import logging
from bson import ObjectId
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

    object_id_str = sys.argv[1]

    # Access the database and collection
    object_id = ObjectId(object_id_str)
    db = client['tpc_survey_f1']
    collection = db['cyclic_server']

    document = collection.find_one({"_id": object_id})

    if document:
        logger.info("Document found:")
        logger.info(document)
    else:
        logger.error(f"No document found with _id: {object_id}")


if __name__ == "__main__":
    main()
