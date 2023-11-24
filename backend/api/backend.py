import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from threading import Thread
from backend_utils import allowed_file, fetch_arxiv_papers, download_papers, process_downloaded_papers, \
    process_uploaded_paper
from backend.mongo.mongo_db import MongoDBHandler

app = Flask(__name__)
mongo_handler = MongoDBHandler()

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload_and_process_pdf', methods=['POST'])
def upload_and_process_pdf():
    # Check if the request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    # If user does not select file, browser submits an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        thread = Thread(target=process_uploaded_paper, args=(mongo_handler, filepath,))
        thread.start()

        return jsonify({"message": "Upload successful"}), 200


@app.route('/list_papers', methods=['GET'])
def list_papers():
    papers = mongo_handler.list_papers()
    titles = [paper['title'] for paper in papers if 'title' in paper]
    return jsonify(titles)


@app.route('/fetch_and_process_arxiv', methods=['POST'])
def fetch_and_process_arxiv():
    theme = request.form.get('theme')
    print(theme)
    papers_metadata = fetch_arxiv_papers(theme, 10)
    print(papers_metadata)
    download_papers(papers_metadata)

    # Start the processing in a background thread
    thread = Thread(target=process_downloaded_papers, args=(mongo_handler, papers_metadata,))
    thread.start()

    return jsonify({"message": "Download started, processing in background", "papers": papers_metadata})


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create upload folder if it doesn't exist
    os.makedirs('../../downloaded_papers', exist_ok=True)  # Create download folder if it doesn't exist
    app.run(debug=True, port=5002)
