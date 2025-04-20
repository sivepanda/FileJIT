import os
import time
import shutil
import requests
from docx import Document
from PyPDF2 import PdfReader

OLLAMA_URL = "http://localhost:11434/api/generate"

class FileClassifier:
    BASE_PATH = "./../root"

    def __init__(self, path):
        self.path = path
        self.content = FileClassifier.read_file(path)
        FileClassifier.classify(self.path, self.content)


    @staticmethod
    def send(message):
        payload = {
            "model": "llama3.2",
            "prompt": message,
            "stream": False
        }
        try:
            response = requests.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            output = result.get("response", "").strip()
            return output
        except Exception as e:
            print(f"❌ Error in sending prompt: {e}")
            return "./"  # Default to root if something fails

    @staticmethod
    def extract_text_from_txt(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def extract_text_from_docx(file_path):
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])

    @staticmethod
    def extract_text_from_pdf(file_path):
        reader = PdfReader(file_path)
        return '\n'.join([page.extract_text() or '' for page in reader.pages])

    @staticmethod
    def read_file(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".txt":
            return FileClassifier.extract_text_from_txt(file_path)
        elif ext == ".docx":
            return FileClassifier.extract_text_from_docx(file_path)
        elif ext == ".pdf":
            return FileClassifier.extract_text_from_pdf(file_path)
        else:
            #assume its a folder now
            new_file_path = os.path.join(file_path, "read.txt")
            return FileClassifier.read_file(new_file_path)

    @staticmethod
    def get_new_file():
        print(f"👀 Watching folder: {FileClassifier.FOLDER_PATH}")
        while True:
            files = [f for f in os.listdir(FileClassifier.FOLDER_PATH)
                     if os.path.isfile(os.path.join(FileClassifier.FOLDER_PATH, f))]
            if files:
                file_path = os.path.join(FileClassifier.FOLDER_PATH, files[0])
                print(f"\n✅ File detected: {files[0]}")
                return file_path, FileClassifier.read_file(file_path)
            time.sleep(1)

    @staticmethod
    def get_context(path):
        context = ""
        folders = [f for f in os.listdir(path)
                   if os.path.isdir(os.path.join(path, f))]

        desc_path = os.path.join(path, "read.txt")
        context += FileClassifier.read_file(desc_path)

        return context.strip(), len(folders) > 0

    @staticmethod
    def move(old, new, content):
        print(f"Are you sure you want to move {old} to {new}")
        response = input("ARE YOU? ")
        if response == 'y':
            if os.path.isdir(old):
                print("DIR UPDATE)")
                shutil.move(old, os.path.join(new, os.path.basename(old)))
                print(f"📦 Moved file to: {new}")
                FileClassifier.update_folder(new, content, old)
            else:
                print("REG UPDATE")
                shutil.move(old, os.path.join(new, os.path.basename(old)))
                print(f"📦 Moved file to: {new}")
                FileClassifier.update(new, content, old)


            
            
        else:
            print("do it yourself then")

    @staticmethod
    def update(path, content, old):
        context, _ = FileClassifier.get_context(path)
        update_message = f"""
You’re a file classifier. Below is the current description of the folder. A new file has been moved into this folder
update the old description to reflect the addition of this new file. KEEP THE RESPONSE WITHIN 10 LINES TOTAL.
Make the entire response better reflect everything in the file. After all, you’ll use this response to classify other files into this folder later.

Old description:
{context}

New file:
{content}
"""
        print(update_message)
        response = FileClassifier.send(update_message)
        print(f"NEW README: {response}")

        res = input("replace read.txt in this directory?")
        if res == 'y':
            with open(os.path.join(path, "read.txt"), 'w', encoding='utf-8') as f:
                f.write(response)


    @staticmethod
    def update_folder(path, content, old):
        #get name of the subfile
        lastindex = max(old.rfind("/"), old.rfind("\\"))
        subfile = old[lastindex + 1:]

        summary_message = f"""
This is a description of what all files and subfolders are contained in this directory. 
Summarize it into 4 lines max. Make it brief and dont waste words like "This current directory" Just say the content

DESCRIPTION:
{content}
"""
        print(summary_message)
        response = FileClassifier.send(summary_message)
        print(f"SUMMARY: {response}")

        with open(os.path.join(path, "read.txt"), 'a', encoding='utf-8') as f:
            f.write(f"\n\n./{subfile}")
            f.write('\n' + response)
            
    @staticmethod
    def classify(path, contents):
        current_path = FileClassifier.BASE_PATH

        while True:
            context, has_subfolders = FileClassifier.get_context(current_path)
            if not has_subfolders:
                break

            prompt = f"""
You're a file classifier. Below is a directory's descriptions with its subfolder descriptions.
Choose the most relevant subfolder for the new file — or return "./" to keep it in the current folder.

This is the new file:"{contents}"

These are the directory and subdirectory descriptions:"{context}"

RETURN ONLY THE MOST RELEVANT DIRECTORY NAME OR "./". NO EXPLANATION
"""
            print(prompt)
            response = FileClassifier.send(prompt)
            print(f"🧠 LLM Suggests: {response} inside {current_path}")
            response = response.strip()
            response = response.lstrip("./")

            if response == "":
                break

            next_path = os.path.join(current_path, response)
            print("SEEING IF: " + next_path, current_path)

            if os.path.isdir(next_path):
                current_path = next_path
            else:
                print(f"⚠️ Invalid directory suggested: {response}. Staying in current directory.")
                break

        FileClassifier.move(path, current_path, contents)


# Run script
# new_file = FileClassifier("./../autosort")
