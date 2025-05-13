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
        self.BASE_PATH= path
        self.content = FileClassifier.read_file(path)
        FileClassifier.classify(self.path, self.content, False)


    @staticmethod
    def send(message):
        payload = {
            "model": "gemma3",
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
        if ext == ".fjit":
            return FileClassifier.extract_text_from_txt(file_path)
        if ext == ".txt":
            return FileClassifier.extract_text_from_txt(file_path)
        elif ext == ".docx":
            return FileClassifier.extract_text_from_docx(file_path)
        elif ext == ".pdf":
            return FileClassifier.extract_text_from_pdf(file_path)
        else:
            #assume its a folder now
            new_file_path = os.path.join(file_path, "description.fjit")
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
    def get_desc(path):
        desc_path = os.path.join(path, "description.fjit")
        desc_content = FileClassifier.read_file(desc_path)
        return desc_content



    @staticmethod
    def get_context(path):
        FOLDER_PATH = path

        #current folder
        context = ""

        folders = [f for f in os.listdir(FOLDER_PATH) if os.path.isdir(os.path.join(FOLDER_PATH, f))]
        folders = [f for f in folders if os.path.exists(os.path.join(os.path.join(path, f), "description.fjit"))]

        for folder in folders:
            full_folder_path = os.path.join(path, folder)
            desc_path = os.path.join(full_folder_path, "description.fjit")
            desc_content = FileClassifier.read_file(desc_path)
            context += f"\n./{folder}: \n{desc_content}\n\n"

        return context, folders

    
    @staticmethod
    def get_context_dict(path):
        FOLDER_PATH = path

        #current folder
        context = dict()

        folders = [f for f in os.listdir(FOLDER_PATH) if os.path.isdir(os.path.join(FOLDER_PATH, f))]
        folders = [f for f in folders if os.path.exists(os.path.join(os.path.join(path, f), "description.fjit"))]

        for folder in folders:
            full_folder_path = os.path.join(path, folder)
            desc_path = os.path.join(full_folder_path, "description.fjit")
            desc_content = FileClassifier.read_file(desc_path)
            context[f"./{folder}"] = desc_content

        return context
    
    @staticmethod
    def move(old, new, content):
        print(f"Are you sure you want to move {old} to {new}")
        response = input("ARE YOU? ")
        if response == 'y':
            if os.path.isdir(old):
                print("DIR UPDATE)")
                shutil.move(old, os.path.join(new, os.path.basename(old)))
                print(f"📦 Moved file to: {new}")
                FileClassifier.update(new, content, old)
            else:
                print("REG UPDATE")
                shutil.move(old, os.path.join(new, os.path.basename(old)))
                print(f"📦 Moved file to: {new}")
                FileClassifier.update(new, content, old)

            
        else:
            print("do it yourself then")

    @staticmethod
    def update(path, content, old):
        context = FileClassifier.get_desc(path)
        update_message = f"""
            You're a directory classifier. Below is the current description of the directory. A new file has been moved into this directory 
            update the old description of this directory to be inclusive of this file. Keep the description short, and with the overall same structure.
            Make the entire response better reflect everything in the file. After all, you'll use this response to classify other files into this folder later.

            Focus on describing the factual contents. Do not use phrases like "I see" or "I notice" or "I'm ready to help".
            Do not ask for more information. Do not include any placeholder responses. Use the following schema for your response:

            Use the following schema:
            ./ [directory description]
            ./[subdirectory0] [subdirectory description]
            ./[subdirectory1] [subdirectory description]
            [continue for all subfolders]...


            Old description:
            {context}

            New file:
            {content}
        """
        print(update_message)
        response = FileClassifier.send(update_message)
        print(f"NEW README: {response}")

        res = input("replace description.fjit in this directory?")
        if res == 'y':
            with open(os.path.join(path, "description.fjit"), 'w', encoding='utf-8') as f:
                f.write(response)

    @staticmethod
    def classify(path, contents, llm_enable = True):
        current_path = FileClassifier.BASE_PATH

        while True:
            context, subfolders = FileClassifier.get_context(current_path)
            if not subfolders:
                break
            if len(subfolders) == 1:
                current_path = os.path.join(current_path, subfolders[0])
                continue
            
            if llm_enable:
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
            else:
               from sentence_transformers import SentenceTransformer, util
               model = SentenceTransformer('all-MiniLM-L6-v2')
               context = FileClassifier.get_context_dict(current_path) 
               context["file"] = contents
               embeddings = {k: model.encode(v, convert_to_tensor=True) for k, v in context.items()}
               similarities = {
                   k: util.cos_sim(embeddings["file"], v).item()
                   for k, v in embeddings.items() if k != "file"
               }

               response = max(similarities, key=similarities.get)

            current_path = os.path.join(current_path, response)


        FileClassifier.move(path, current_path, contents)


# Run script
