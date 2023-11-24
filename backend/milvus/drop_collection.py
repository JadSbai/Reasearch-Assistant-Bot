from pymilvus import connections, Collection, utility

# Establish connection with Milvus server
connections.connect()

collection_name = "paragraph"

# Check if the collection exists
if utility.has_collection(collection_name):
    # Load the collection
    collection = Collection(name=collection_name)

    # Drop the collection
    collection.drop()
    print(f"Collection '{collection_name}' dropped successfully.")
else:
    print(f"Collection '{collection_name}' does not exist.")

