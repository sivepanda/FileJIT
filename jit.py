import os
import time
import shutil
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

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


def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"❌ Failed to read {path}: {e}")
        return ""


def get_new_file():
    FOLDER_PATH = "./autosort"
    print(f"👀 Watching folder: {FOLDER_PATH}")

    while True:
        files = [f for f in os.listdir(FOLDER_PATH) if os.path.isfile(os.path.join(FOLDER_PATH, f))]
        if files:
            file_path = os.path.join(FOLDER_PATH, files[0])
            print(f"\n✅ File detected: {files[0]}")
            return file_path, read_file(file_path)
        time.sleep(1)


def get_context(path):
    context = ""
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

    # Try to read current directory's desc.txt
    desc_path = os.path.join(path, "desc.txt")
    context += read_file(desc_path)

    return context.strip(), len(folders) > 0


def move(old, new, content):
    print(f"Are you sure you want to move {old} to {new}")
    response = input("ARE YOU?")
    if response == 'y':
        shutil.move(old, os.path.join(new, os.path.basename(old)))
        print(f"📦 Moved file to: {new}")
        update(new, content)
    else:
        print("do it yourself then")

def update(path, content):
    context, _ = get_context(path)
    update_messege = f"""
Youre a file classifier. Below is the current description of the folder. A new file has been moved into this folder
update the old description to reflect the addition of this new file. KEEP THE RESPONSE WITHIN 4 LINES TOTAL

Old description:
{context}

New file:
{content}"""

    print(update_messege)
    response = send(update_messege)
    print(f"NEW README: {response}")


def classify(path, contents):
    base_path = "./root"
    current_path = base_path

    while True:
        context, has_subfolders = get_context(current_path)
        if not has_subfolders:
            break

        prompt = f"""
You're a file classifier. Below is a directory's descriptions with its subfolder descriptions.
Choose the most relevant subfolder for the new file — or return "./" to keep it in the current folder.

ONLY RETURN ONE OF THE SUBDIRECTORY NAMES OR "./".

--- Directory Context ---
{context}

--- New File ---
{contents}
"""
        
        print(prompt)
        response = send(prompt)
        print(f"🧠 LLM Suggests: {response} inside {current_path}")
        response = response.strip()
        response = response.lstrip("./")

        if response == "":
            break

        print(response)
        next_path = os.path.join(current_path, response)
        print("SEEING IF: " + next_path, current_path)

        if os.path.isdir(next_path):
            current_path = next_path
        else:
            print(f"⚠️ Invalid directory suggested: {response}. Staying in current directory.")
            break

    move(path, current_path, contents)



if __name__ == "__main__":
    new_path, new_file = get_new_file()
    classify(new_path, new_file)
