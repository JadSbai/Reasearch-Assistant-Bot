# Research Assistant Bot

## Project Overview
The Research Bot Assistant is a sophisticated tool designed for researchers, academics, and students, transforming their interaction with academic literature to deliver a seamless and intuitive research experience.

Key Features:
1. **Paper Upload and Query**: Users can upload multiple academic papers in PDF format. Utilizing a custom processing pipeline, the bot extracts information section-by-section from these unstructured documents, converting it into structured data. This data is stored in MongoDB for efficient retrieval.

2. **Automatic Paper Retrieval**: For a specified research theme, the bot autonomously retrieves 20 relevant papers directly from Arxiv.

Technical Functionalities:
- **Enhanced Data Processing**: The bot processes unstructured PDF data into structured formats, stored in MongoDB. This ensures efficient data management and retrieval.

- **Milvus Vector Database Integration**: A key component is the integration of Milvus, a vector database, which enables sophisticated vector search capabilities. This feature allows the bot to do more than just summarizing; it can synthesize information, combining ideas from various papers, comparing methods, and identifying gaps in existing research.

- **GPT-4 Powered Responses**: Utilizing OpenAI's GPT-4, the bot provides highly relevant and contextually rich responses to user queries, drawing knowledge straight from the papers. 

- **Intuitive Interface with Gradio**: The user interface, built with Gradio, is designed for ease of use, allowing users to upload papers, specify research themes, and interact with the bot without hassle.

- **Automated and Integrated Workflow**: The entire workflow, from data extraction to sophisticated query processing, is automated and facilitated through API calls between two distinct services.

## Demo

[![Demo Video](https://img.youtube.com/vi/V3w9wzue95o/0.jpg)](https://www.youtube.com/watch?v=V3w9wzue95o)
