import os
import time
import shutil
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"  # Default Ollama endpoint

def classify(message):
    payload = {
        "model": "llama3.2",  # or "llama3:latest" if that's your tag
        "prompt": message,
        "stream": False  # easier to parse if we don't stream
    }

    print("💬 Sending prompt to Ollama...")
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    result = response.json()
    output = result.get("response", "").strip()

    print("🧠 LLaMA says:")
    print(output)
    return output


def read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        contents = file.read()
        # print(contents)
        return contents


# def get_new_file():
#     FOLDER_PATH = "./autosort"

#     print(f"👀 Watching folder: {FOLDER_PATH}")

#     file_name = None
#     while not file_name:
#         files = [f for f in os.listdir(FOLDER_PATH) if os.path.isfile(os.path.join(FOLDER_PATH, f))]
#         if files:
#             file_name = files[0]
#         else:
#             time.sleep(1)

#     file_path = os.path.join(FOLDER_PATH, file_name)

#     print(f"\n✅ File detected: {file_name}\n")

#     return file_path, read_file(file_path)


# def get_context():
#     FOLDER_PATH = "./root"

#     folders = [os.path.join(FOLDER_PATH, f) for f in os.listdir(FOLDER_PATH)]
#     print(f"📁 Found folders: {folders}")

#     context = ""
#     for folder in folders:
#         desc_path = os.path.join(folder, "desc.txt")
#         desc_content = read_file(desc_path)
#         context += f"{folder}: {desc_content}\n"

#     return context


# def move(old, new):
#     os.makedirs(new, exist_ok=True)
#     shutil.move(old, os.path.join(new, os.path.basename(old)))
#     print(f"📦 Moved file to: {new}")


# # MAIN FLOW
# context = get_context()
# new_path, new_file = get_new_file()

# message = f"""Gemini, I'm going to give you names of folders and their description.
# {context}
# Tell me what folder this new file belongs to:
# {new_file}
# Return only the folder file path. Don't explain anything else."""

# destination = classify(message)
# print("DESTINATION:", destination)

# move(new_path, destination)

def get_new_folder():
    FOLDER_PATH = "./autosort"

    print(f"👀 Watching folder: {FOLDER_PATH}")

    item_name = None
    while not item_name:
        items = [f for f in os.listdir(FOLDER_PATH) if os.path.isdir(os.path.join(FOLDER_PATH, f))]
        if items:
            item_name = items[0]

            item_path = os.path.join(FOLDER_PATH, item_name)
               
        else:
            time.sleep(1)

    folder_path = os.path.join(FOLDER_PATH, item_name)

    print(f"\n✅ Folder detected: {item_name}\n")

    return folder_path


old_path = get_new_folder()

def write_desc(context, path_name):
    
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
    

    return classify(system_prompt)

def find_content(old_path, all_folders):
    context = ""
    for root, dirs, files in os.walk(old_path):
        if all_folders:
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)

                text_dir_path = os.path.join(dir_path, "read.txt")
                if os.path.exists(text_dir_path):
                    context += str(dir_path) + " " + read_file(text_dir_path) + "\n"
                else:
                    context += str(dir_path) + " " + generate_text(dir_path) + "\n"
        
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    words = content.split()
                    
                    excerpt = ' '.join(words[:500])
                    
                    context += f"{dir_path} {excerpt}\n"
                
                print("context ", context)
                    
            except Exception as e:
                context += f"File: {file_path}\n"
                context += f"Could not extract content: {str(e)}\n\n"
    return context

def generate_text(old_path):
    read_me = os.path.join(old_path, "read.txt")
    description = ""
    if not os.path.exists(read_me):
        try:
            with open(read_me, "w") as file:
                all_folders = False
                print("Would you like only to have a read me for this folder or all sub-folders as well? (y) for all; (n) for none")
                action = input("Enter action for folder: ")
                if action == "y":
                    all_folders = True
                text_message = find_content(old_path, all_folders)
                description = write_desc(text_message, old_path)

                file.write(description)
                print(f"File '{read_me}' created successfully in '{old_path}'.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        description = read_file(read_me)
    return description


print(generate_text(old_path))