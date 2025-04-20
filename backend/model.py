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
    
    try:
        items = os.listdir(old_path)
        
        # Process directories first
        dirs = [item for item in items if os.path.isdir(os.path.join(old_path, item))]
        for dir_name in dirs:
            dir_path = os.path.join(old_path, dir_name)
            
            text_dir_path = os.path.join(dir_path, "read.txt")
            if os.path.exists(text_dir_path):
                context += str(dir_path) + " " + read_file(text_dir_path) + "\n"
            elif all_folders:
                context += str(dir_path) + " " + generate_text(dir_path) + "\n"
        
        # Process files
        files = [item for item in items if os.path.isfile(os.path.join(old_path, item))]
        for file_name in files:
            file_path = os.path.join(old_path, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    words = content.split()
                    excerpt = ' '.join(words[:500])
                    context += f"{old_path} {excerpt}\n"
                
                print("context ", context)
                    
            except Exception as e:
                context += f"File: {file_path}\n"
                context += f"Could not extract content: {str(e)}\n\n"
                
    except Exception as e:
        context += f"Error accessing directory {old_path}: {str(e)}\n"
    
    return context

def generate_text(old_path):
    read_me = os.path.join(old_path, "read.txt")
    description = ""
    if not os.path.exists(read_me):
        try:
            with open(read_me, "w") as file:
                all_folders = False
                print(f"Would you like only to have a read me for this folder ({old_path}) or all sub-folders as well? (y) for all; (n) for none")
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
