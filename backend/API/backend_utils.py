import asyncio
import os

import requests
import xml.etree.ElementTree as ET

from backend.data_processing import insert_and_process_pdf

MILVUS_URL = "https://eed8-2a00-23c6-54e7-2c01-ddd6-167e-8696-b759.ngrok-free.app/insert"
ALLOWED_EXTENSIONS = {'pdf'}


def fetch_arxiv_papers(query, max_results=10):
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results
    }

    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)

    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
        link = entry.find("{http://www.w3.org/2005/Atom}link[@title='pdf']")
        authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in
                   entry.findall('{http://www.w3.org/2005/Atom}author')]
        pdf_url = link.attrib['href'] if link is not None else "No PDF URL found"
        papers.append({"title": title, "summary": summary, "pdf_url": pdf_url, "author": authors})

    return papers


def process_downloaded_papers(mongo_handler, papers_metadata):
    directory = 'downloaded_papers/'
    for metadata in papers_metadata:
        title = metadata['title']
        author = metadata['author']
        # Assuming the filename is derived from the title
        filename = title + '.pdf'
        file_path = os.path.join(directory, filename)

        if os.path.exists(file_path):
            print(f"Processing: {title}")
            sections, title, author = insert_and_process_pdf(mongo_handler, file_path, title, author)
            # send_paragraphs_to_milvus(title, author, sections)
            send_paragraphs_to_milvus(title, author, sections)
            print(f"Processed: {title}")
        else:
            print(f"File not found for: {title}")


def process_uploaded_paper(mongo_handler, filepath):
    # Process the PDF and store in MongoDB
    sections, title, author = insert_and_process_pdf(mongo_handler, filepath)
    print(f"Processed: ")
    # Send paragraphs to Milvus
    # send_paragraphs_to_milvus(title, author, sections)
    asyncio.run(send_paragraphs_to_milvus(title, author, sections))


def download_papers(papers_metadata):
    for paper in papers_metadata:
        pdf_url = paper['pdf_url']
        if pdf_url != "No PDF URL found":
            file_path = download_paper(pdf_url, paper['title'])
            if file_path:
                # Implement the processing logic here
                print(f"Downloaded and processed: {file_path}")
            else:
                print(f"Failed to download paper: {paper['title']}")


def download_paper(pdf_url, title):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        file_path = os.path.join('../../downloaded_papers', f"{title}.pdf")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    else:
        return None


def send_paragraphs_to_milvus(title, author, sections):
    success_count = 0
    error_count = 0
    error_messages = []
    for section, paragraphs in sections.items():
        for paragraph in paragraphs:
            paragraph_data = {
                "paper_title": title,
                "paper_author": author,
                "paragraph_text": paragraph,
                "section_type": section,
            }
            # Send the data to Milvus
            try:
                response = requests.post(MILVUS_URL, json=paragraph_data)

                # Check if the request was successful
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
                    error_messages.append(
                        f"Failed to insert paragraph in section '{section}'. Response: {response.text}")

            except requests.RequestException as e:
                error_count += 1
                error_messages.append(f"Request failed for paragraph in section '{section}'. Error: {str(e)}")

    return {
        "status": "completed",
        "success_count": success_count,
        "error_count": error_count,
        "errors": error_messages
    }

# async def send_paragraphs_to_milvus(title, author, sections):
#     success_count = 0
#     error_count = 0
#     error_messages = []
#     print(title, author)
#
#     async with aiohttp.ClientSession() as session:
#         for section, paragraphs in sections.items():
#             print(section)
#             for paragraph in paragraphs:
#                 paragraph_data = {
#                     "paper_title": title,
#                     "paper_author": author,
#                     "paragraph_text": paragraph,
#                     "section_type": section,
#                 }
#                 # Send the data to Milvus
#                 try:
#                     async with session.post(MILVUS_URL, json=paragraph_data) as response:
#                         # Check if the request was successful
#                         if response.status == 200:
#                             success_count += 1
#                         else:
#                             error_count += 1
#                             response_text = await response.text()
#                             error_messages.append(
#                                 f"Failed to insert paragraph in section '{section}'. Response: {response_text}")
#
#                 except aiohttp.ClientError as e:
#                     error_count += 1
#                     error_messages.append(f"Request failed for paragraph in section '{section}'. Error: {str(e)}")
#
#     return {
#         "status": "completed",
#         "success_count": success_count,
#         "error_count": error_count,
#         "errors": error_messages
#     }


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
