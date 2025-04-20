import os
import time
import shutil
import requests

class Folder:
    def __init__(self, autosort_path="./../autosort", model="llama3.2", ollama_url="http://localhost:11434/api/generate"):
        self.autosort_path = autosort_path
        self.model = model
        self.ollama_url = ollama_url
        
        # Create autosort directory if it doesn't exist
        os.makedirs(self.autosort_path, exist_ok=True)
    
    def classify(self, message):
        """Use Ollama to classify/generate text"""
        payload = {
            "model": self.model,
            "prompt": message,
            "stream": False
        }

        print("💬 Sending prompt to Ollama...")
        response = requests.post(self.ollama_url, json=payload)
        response.raise_for_status()

        result = response.json()
        output = result.get("response", "").strip()

        print("🧠 LLaMA says:")
        print(output)
        return output
    
    def read_file(self, path):
        """Read file contents"""
        with open(path, 'r', encoding='utf-8') as file:
            contents = file.read()
            return contents
    
    # def get_new_folder(self):
    #     """Watch the autosort directory for a new folder"""
    #     print(f"👀 Watching folder: {self.autosort_path}")

    #     item_name = None
    #     while not item_name:
    #         items = [f for f in os.listdir(self.autosort_path) if os.path.isdir(os.path.join(self.autosort_path, f))]
    #         if items:
    #             item_name = items[0]
    #             item_path = os.path.join(self.autosort_path, item_name)
    #         else:
    #             time.sleep(1)

    #     folder_path = os.path.join(self.autosort_path, item_name)
    #     print(f"\n✅ Folder detected: {item_name}\n")
    #     return folder_path
    
    def write_desc(self, context, path_name):
        """Generate directory description using Ollama"""
        system_prompt = f"""
        You are an assistant that creates concise directory descriptions.
        
        DIRECTORY PATH: {path_name}
        
        SUBDIRECTORY CONTENTS:
        {context}
        
        Using ONLY the information above, write a single paragraph (5-7 sentences) describing:
        1. What this directory appears to contain
        2. What its likely purpose is
        3. How the contents relate to each other
        4. What subject matter or field this directory pertains to
        
        Focus on describing the factual contents. Do not use phrases like "I see" or "I notice" or "I'm ready to help".
        Do not ask for more information. Do not include any placeholder responses.
        """
        
        return self.classify(system_prompt)
    
    def find_content(self, folder_path, all_folders):
        """Find content in the folder to describe"""
        context = ""
        
        try:
            items = os.listdir(folder_path)
            
            # Process directories first
            dirs = [item for item in items if os.path.isdir(os.path.join(folder_path, item))]
            for dir_name in dirs:
                dir_path = os.path.join(folder_path, dir_name)
                
                text_dir_path = os.path.join(dir_path, "read.txt")
                if os.path.exists(text_dir_path):
                    context += str(dir_path) + " " + self.read_file(text_dir_path) + "\n"
                elif all_folders:
                    context += str(dir_path) + " " + self.generate_text(dir_path) + "\n"
            
            # Process files
            files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]
            for file_name in files:
                file_path = os.path.join(folder_path, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        words = content.split()
                        excerpt = ' '.join(words[:500])
                        context += f"{folder_path} {excerpt}\n"
                    
                    print("context ", context)
                        
                except Exception as e:
                    context += f"File: {file_path}\n"
                    context += f"Could not extract content: {str(e)}\n\n"
                    
        except Exception as e:
            context += f"Error accessing directory {folder_path}: {str(e)}\n"
        
        return context
    
    def generate_text(self, folder_path, process_all_subfolders=None):
        """Generate description for folder"""
        if not os.path.isdir(folder_path):
            return ""

        read_me = os.path.join(folder_path, "read.txt")
        description = ""
        
        if not os.path.exists(read_me):
            try:
                with open(read_me, "w") as file:
                    all_folders = False
                    
                    # Only ask for input if process_all_subfolders parameter wasn't provided
                    if process_all_subfolders is None:
                        print(f"Would you like only to have a read me for this folder ({folder_path}) or all sub-folders as well? (y) for all; (n) for none")
                        action = input("Enter action for folder: ")
                        if action == "y":
                            all_folders = True
                    else:
                        all_folders = process_all_subfolders
                    
                    text_message = self.find_content(folder_path, all_folders)
                    description = self.write_desc(text_message, folder_path)

                    file.write(description)
                    print(f"File '{read_me}' created successfully in '{folder_path}'.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            description = self.read_file(read_me)
        
        return description
    
    # def run(self, process_all_subfolders=None):
    #     """Main method to run the autosort process"""
    #     # folder_path = self.get_new_folder()
    #     return self.generate_text(folder_path, process_all_subfolders)


# If run directly, demonstrate usage
# if __name__ == "__main__":
#     sorter = Folder()
#     sorter.run()