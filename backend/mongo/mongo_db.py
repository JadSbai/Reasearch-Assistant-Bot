from pymongo import MongoClient
from bson import binary


class MongoDBHandler:
    def __init__(self, uri="mongodb+srv://Jad:Lifesgood05$@cluster0.y4bz1mr.mongodb.net/?retryWrites=true&w=majority", db_name="ResearchAssistant"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.papers_collection = self.db["papers"]
        self.paragraphs_collection = self.db["paragraphs"]

    def insert_paper(self, title, filepath, plaintext, author):
        with open(filepath, "rb") as file:
            binary_data = file.read()
        paper = {
            "title": title,
            "content": binary.Binary(binary_data),
            "plaintext": plaintext,
            "author": author,
        }
        return self.papers_collection.insert_one(paper).inserted_id

    def insert_paragraph(self, paper_id, text, section_name, previous_paragraph_id=None):
        paragraph = {
            'text': text,
            'section': section_name,
            'previous_paragraph': previous_paragraph_id,
            'next_paragraph': None,
            'paper': paper_id,
        }
        return self.paragraphs_collection.insert_one(paragraph).inserted_id

    def update_paragraph_next(self, prev_paragraph_id, next_paragraph_id):
        self.paragraphs_collection.update_one(
            {'_id': prev_paragraph_id},
            {'$set': {'next_paragraph': next_paragraph_id}}
        )

    def find_paper_by_id(self, paper_id):
        return self.papers_collection.find_one({"_id": paper_id})

    def list_papers(self):
        return self.papers_collection.find({}, {"title": 1, "_id": 0})

    def find_paragraphs_by_paper_id(self, paper_id):
        return self.paragraphs_collection.find({"paper_id": paper_id})
