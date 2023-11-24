from pymilvus import connections, Collection, Index, IndexType

connections.connect()
collection_name = "paragraph"
collection = Collection(name=collection_name)

# Define the index type and parameters
index_params = {
    "index_type":"IVF_FLAT",	 # Choose an appropriate index type for your use case
    "metric_type": "L2",  # or "IP", depending on your use case
    "params": {"nlist": 1024}
}

# Create the index
index = Index(collection, field_name="paragraph_embedding", index_params=index_params)