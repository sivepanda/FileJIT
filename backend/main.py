import os
import time
import shutil
import requests
from folder import Folder
from fileClassifier import FileClassifier
# import filesearch as fl

autosort_path="./../autosort"
root_path = "./../root"

# res = input("Would you like to search for a file or add a file")
# if res == "s":
#     fl.main()
f = Folder()
f.generate_text(root_path)
print("done")

def get_new_folder():
    """Watch the autosort directory for a new folder"""
    # while True:
    print(f"👀 Watching folder: {autosort_path}")

    item_name = None
    while not item_name:
        print("testing ")
        items = [f for f in os.listdir(autosort_path)]
        if items:
            item_name = items[0]
            item_path = os.path.join(autosort_path, item_name)
        else:
            time.sleep(1)

    folder_path = os.path.join(autosort_path, item_name)

    print(f"\n✅ Folder detected: {item_name}\n")

    classify = FileClassifier(root_path)
    # text = Folder()
    # text.generate_text(folder_path)
    print("iteration done")

get_new_folder()




