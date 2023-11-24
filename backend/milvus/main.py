from flask import Flask, request, jsonify
from pymilvus import Collection, connections
import requests

app = Flask(__name__)
app.config['ALLOWED_HOSTS'] = '*'


collection_name = "paragraph"
conn = connections.connect(host="127.0.0.1", port=19530)
collection = Collection(name=collection_name)

def query(texts, model_id, hf_token):
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(api_url, headers=headers, json={"inputs": texts, "options": {"wait_for_model": True}})
    return response.json()

@app.route('/insert', methods=['POST'])
def insert_document():
    data = request.json
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    hf_token = "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"

    embeddings = query([data['paragraph_text']], model_id, hf_token)

    data['paragraph_embedding'] = embeddings[0][:128]
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        collection.insert(data)

        return jsonify({"message": "Document inserted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_similar_paragraphs():
    collection.load()
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    query_text = data['text']
    number_documents = data.get('number_documents', 10)

    query_text = data['text']

    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    hf_token = "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"

    embeddings = query([query_text], model_id, hf_token)

    query_embedding = embeddings[0][:128]

    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    search_results = collection.search(
        data=[query_embedding],
        anns_field="paragraph_embedding",
        param=search_params,
        limit=number_documents,
        output_fields = ["paper_author", "paper_title", "paragraph_text", "section_type"],
        expr=None,
        consistency_level="Strong"
    )

    # Extract IDs and distances
    records = [
        {
			"id": hit.id,
            "paper_author": hit.entity.get("paper_author"),
            "paper_title": hit.entity.get("paper_title"),
            "paragraph_text": hit.entity.get("paragraph_text"),
            "section_type": hit.entity.get("section_type"),
            "distance": hit.distance
		} for hit in search_results[0]
    ]

    return jsonify(records)

if __name__ == '__main__':
    app.run(port=5003,debug=True)
