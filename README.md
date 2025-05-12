# FileJIT

## Overview
The **FileJIT** project is a file search and retrieval system that leverages AI-powered embeddings and similarity search to classify/organize files into a file directory, as well as find the most relevant files based on conversational prompting.

This project is designed to handle human-readable files and provide ranked suggestions for the closest matches based on a user-provided query.

This repository holds the most up-to-date version of the software initially developed by myself, as well as the team I was on for the *8vc Hackathon* at Duke.

---

## Features
- **File Embedding Generation**: Converts file contents into dense vector embeddings using a pre-trained SentenceTransformer model.
- **Similarity Search**: Uses FAISS to perform fast and efficient similarity searches for the closest file matches.
- **Top-N Results**: Returns the top 3 most relevant files for a given query.
- **Dynamic File System Scanning**: Automatically scans a specified directory for files and processes their contents.
- **Persistence**: Supports saving and loading FAISS indices for reuse without regenerating embeddings.

---

## Technologies Used
- **Tauri / Svelte**
- **Python 3.12**
- **FAISS**: For similarity search and clustering.
- **SentenceTransformers**: For generating embeddings from text.
- **OS Module**: For file system traversal.
- **Requests**: For potential API integrations (e.g., classification or external services).

---

## Installation

1. **Clone the Repository**:
```bash
   git clone https://github.com/your-repo/8vcHackathon.git
   cd 8vcHackathon
   ```
2. **Install Dependencies**: Ensure you have Python 3.12 installed. Then, install the required Python packages:
 ```bash
   pip install -r requirements.txt
   ```
