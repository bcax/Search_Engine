Search Engine Project
Overview
This project is a basic search engine implemented using Python. It consists of two main components:

M1 (Indexer): Responsible for indexing a collection of 50,000+ URLs saved in a folder. It processes the text content from the URLs, tokenizes the words, applies stemming, and creates an inverted index.

M2 (Search Component): This module handles user queries by searching through the prebuilt index to find relevant results. It ranks documents using a weighted scoring mechanism based on TF-IDF values and field importance (e.g., title, body, headings).

Components
M1.py (Indexer)
This component performs the following functions:

Text Processing: Extracts and cleans content from URLs, tokenizing and stemming words using the Porter2 Stemmer.
Inverted Index Creation: Builds an inverted index for the corpus. For each word in the corpus, a posting list is created, which contains document IDs and term frequency in different fields (title, body, headings).
TF-IDF Calculation: Computes the Term Frequency-Inverse Document Frequency (TF-IDF) value for each term in each document.
Index Serialization: Saves the index and associated metadata (document IDs and offsets) in multiple parts as JSON files to optimize for large-scale data.
M2.py (Search Component)
This component provides the search functionality, including:

Query Processing: Takes user input, processes the query using tokenization and stemming, and searches for matching terms in the index.
Scoring and Ranking: Uses the TF-IDF scores to rank documents. Results are further refined by weighting the importance of specific fields (e.g., title has a higher weight than the body text).
Web Interface: A web-based interface built with Flask to handle user search queries and display results.
How It Works
Indexing:

Run M1.py to create an inverted index from the 50,000+ URLs located in the specified folder (developer/DEV).
This script will process the content, tokenize it, and create an index. The index will be stored across multiple files (index_table_part_X.json) along with additional metadata like the file-to-docID mappings.
Searching:

The search component (M2.py) can be run to start a Flask web application.
When a user submits a query, the system processes the input, checks the index for matching documents, and returns the top 10 results ranked by relevance.
Results are displayed along with the time taken to complete the search.
