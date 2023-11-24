from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections

# Define fields including a primary key
id_field = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True)
paper_title = FieldSchema(name="paper_title", dtype=DataType.VARCHAR, max_length=20000, default_value="")
paper_author = FieldSchema(name="paper_author", dtype=DataType.VARCHAR, max_length=20000, default_value="")
section_type = FieldSchema(name="section_type", dtype=DataType.VARCHAR, max_length=20000, default_value="")
paragraph_text = FieldSchema(name="paragraph_text", dtype=DataType.VARCHAR, max_length=20000, default_value="")
paragraph_embedding = FieldSchema(name="paragraph_embedding", dtype=DataType.FLOAT_VECTOR, dim=128)

# Create a schema with the primary key
schema = CollectionSchema(
    fields=[id_field, paper_title, paper_author, section_type, paragraph_text, paragraph_embedding],
    description="Paragraph search",
    enable_dynamic_field=True
)

collection_name = "paragraph"
connections.connect(host='localhost', port='19530')

# Initialize the collection
collection = Collection(name=collection_name, schema=schema, using='default', shards_num=2)

