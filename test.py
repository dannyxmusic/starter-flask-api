# import sys
# from pymongo import MongoClient
# import os
# from bson import ObjectId

# # MongoDB Atlas connection URI
# MONGO_URI = os.environ.get('MONGO_URI')
# client = MongoClient(MONGO_URI)

# # Access the database and collection
# db = client['tpc_survey_f1']
# collection = db['cyclic_server']

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python test.py <insert_id>")
#         sys.exit(1)

#     insert_id = sys.argv[1]

#     # Convert insert_id to ObjectId
#     try:
#         insert_id = ObjectId(insert_id)
#     except Exception as e:
#         print(f"Error converting insert_id to ObjectId: {e}")
#         sys.exit(1)

#     # Find document with the given insert_id
#     document = collection.find_one({"_id": insert_id})

#     if document:
#         print(f"Document found: {document}")
#     else:
#         print("Document not found")

import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test.py <insert_id>")
        sys.exit(1)

    insert_id = sys.argv[1]
    print(f"Insert ID received as command-line argument: {insert_id}")
