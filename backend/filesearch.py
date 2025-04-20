from sentence_transformers import SentenceTransformer
import faiss
import os

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and fast

def generate_embeddings(base_path):
    file_paths = []
    file_contents = []

    # Traverse the file system
    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_paths.append(file_path)
                    file_contents.append(content)
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

    # Search for the closest match
    distances, indices = index.search(query_embedding, k=1)  # Retrieve top-1 match

    # Get the closest file path
    closest_file = file_paths[indices[0][0]]
    return closest_file, distances[0][0]


def main():
    base_path = "./autosort"  # Root directory to scan
    print("Generating embeddings for files...")
    index, file_paths = generate_embeddings(base_path)

    print("Embeddings generated. Ready for search.")
    while True:
        query = input("\nEnter your search query: ")
        closest_file, distance = search_files(query, index, file_paths)
        print(f"Closest match: {closest_file} (Distance: {distance})")