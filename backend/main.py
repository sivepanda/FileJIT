import os
import time
import shutil
import requests
from folder import Folder

autosort_path="./../autosort"
def get_new_folder():
    """Watch the autosort directory for a new folder"""
    print(f"👀 Watching folder: {autosort_path}")

    item_name = None
    while not item_name:
        items = [f for f in os.listdir(autosort_path) if os.path.isdir(os.path.join(autosort_path, f))]
        if items:
            item_name = items[0]
            item_path = os.path.join(autosort_path, item_name)
        else:
            time.sleep(1)

    folder_path = os.path.join(autosort_path, item_name)

    print(f"\n✅ Folder detected: {item_name}\n")

    return folder_path

classify = Folder()

old_path = get_new_folder()
classify.generate_text(old_path)
