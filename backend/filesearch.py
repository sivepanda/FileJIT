from sentence_transformers import SentenceTransformer
import faiss
import os
import PyPDF2  
from docx import Document  

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and fast


def generate_embeddings(base_path):
    file_paths = []
    file_contents = []

    print(base_path)
    # Traverse the file system
    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            print("file path: ", file_path)
            try:
                if file.lower().endswith('.pdf'):  # Check if the file is a PDF
                    # Extract text from PDF
                    with open(file_path, 'rb') as pdf_file:
                        reader = PyPDF2.PdfReader(pdf_file)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text()
                        file_contents.append(content)
                        file_paths.append(file_path)
                elif file.lower().endswith('.docx'):  # Check if the file is a Word document
                    # Extract text from Word document
                    doc = Document(file_path)
                    content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                    file_contents.append(content)
                    file_paths.append(file_path)
                else:
                    # Handle plain text files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_contents.append(content)
                        file_paths.append(file_path)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Generate embeddings for file contents
    embeddings = model.encode(file_contents, convert_to_tensor=False)

    # Initialize FAISS index
    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)  # Add embeddings to the index

    return index, file_paths


def search_files(query, index, file_paths):
    # Generate embedding for the query
    query_embedding = model.encode([query], convert_to_tensor=False)

    # Search for the top 3 closest matches
    distances, indices = index.search(query_embedding, k=3)  # Retrieve top 3 closest matches

    # Get the top 3 file paths and their distances
    results = [(file_paths[indices[0][i]], distances[0][i]) for i in range(len(indices[0]))]
    return results


def main():
    base_path = "C:/Users/darre/VSCode Projects/8vcHackathon/testdirectory"  # Root directory to scan
    print("Generating embeddings for files...")
    index, file_paths = generate_embeddings(base_path)

    print("Embeddings generated. Ready for search.")
    while True:
        query = input("\nEnter your search query: ")
        results = search_files(query, index, file_paths)

        print("\nTop 3 matches:")
        for i, (file_path, distance) in enumerate(results):
            print(f"{i + 1}. {file_path} (Distance: {distance})")
if __name__ == "__main__":
    main()