# from sentence_transformers import SentenceTransformer
# import faiss
# import os

# # Initialize the embedding model
# model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and fast

# def generate_embeddings(base_path):
#     file_paths = []
#     file_contents = []

#     print(base_path)
#     # Traverse the file system
#     for root, _, files in os.walk(base_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             print("file path: ", file_path)
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     content = f.read()
#                     file_paths.append(file_path)
#                     file_contents.append(content)
#             except Exception as e:
#                 print(f"Error reading {file_path}: {e}")

#     # Generate embeddings for file contents
#     embeddings = model.encode(file_contents, convert_to_tensor=False)

#     # Initialize FAISS index
#     dimension = embeddings[0].shape[0]
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings)  # Add embeddings to the index

#     return index, file_paths


# def search_files(query, index, file_paths):
#     # Generate embedding for the query
#     query_embedding = model.encode([query], convert_to_tensor=False)

#     # Search for the top 3 closest matches
#     distances, indices = index.search(query_embedding, k=3)  # Retrieve top 3 closest matches

#     # Get the top 3 file paths and their distances
#     results = [(file_paths[indices[0][i]], distances[0][i]) for i in range(len(indices[0]))]
#     return results


# def main():
#     base_path = "./../root"  # Root directory to scan
#     print("Generating embeddings for files...")
#     index, file_paths = generate_embeddings(base_path)

#     print("Embeddings generated. Ready for search.")
#     while True:
#         query = input("\nEnter your search query: ")
#         results = search_files(query, index, file_paths)

#         print("\nTop 3 matches:")
#         for i, (file_path, distance) in enumerate(results):
#             print(f"{i + 1}. {file_path} (Distance: {distance})")
# # if __name__ == "__main__":
# #     main()

from sentence_transformers import SentenceTransformer
import faiss
import os

class EmbeddingHandler:
    def __init__(self, base_path):
        self.base_path = base_path
        self.index = None
        self.file_paths = None
        # Initialize the embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and fast model
    
    def generate_embeddings(self):
        """
        Generate embeddings for all files in the base_path directory.
        Returns True if successful, False otherwise.
        """
        file_paths = []
        file_contents = []

        print(f"Scanning directory: {self.base_path}")
        
        # Traverse the file system
        for root, _, files in os.walk(self.base_path):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_paths.append(file_path)
                        file_contents.append(content)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        if not file_contents:
            print("No files were found or could be read.")
            return False

        try:
            # Generate embeddings for file contents
            print(f"Generating embeddings for {len(file_contents)} files...")
            embeddings = self.model.encode(file_contents, convert_to_tensor=False)

            # Initialize FAISS index
            dimension = embeddings[0].shape[0]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings)  # Add embeddings to the index
            self.file_paths = file_paths
            
            print("Embeddings successfully generated and indexed.")
            return True
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return False

    def search_files(self, query, k=3):
        """
        Search for files similar to the query.
        Returns a list of tuples (file_path, distance).
        """
        if self.index is None or self.file_paths is None:
            print("Search index not initialized. Call generate_embeddings() first.")
            return []
            
        try:
            # Generate embedding for the query
            query_embedding = self.model.encode([query], convert_to_tensor=False)

            # Search for the top k closest matches
            k = min(k, len(self.file_paths))  # Make sure k is not larger than the number of files
            distances, indices = self.index.search(query_embedding, k=k)

            # Get the top k file paths and their distances
            results = [(self.file_paths[indices[0][i]], float(distances[0][i])) 
                      for i in range(len(indices[0]))]
            return results
        except Exception as e:
            print(f"Error during search: {e}")
            return []

def main():
    """
    Standalone function to demonstrate the use of the EmbeddingHandler.
    """
    base_path = "./../../root"
    print("Generating embeddings for files...")
    handler = EmbeddingHandler(base_path)
    handler.generate_embeddings()

    print("Embeddings generated. Ready for search.")
    while True:
        query = input("\nEnter your search query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
            
        results = handler.search_files(query)

        print("\nTop 3 matches:")
        for i, (file_path, distance) in enumerate(results):
            print(f"{i + 1}. {file_path} (Distance: {distance:.4f})")

if __name__ == "__main__":
    main()