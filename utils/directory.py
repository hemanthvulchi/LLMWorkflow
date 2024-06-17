import os

def get_current_directory():
    return os.getcwd()

def get_db_filepath(persist_directory):
    return os.path.join(persist_directory, "chroma.sqlite3") 

def check_directory(directory_name):
    directory_path = os.path.join(get_current_directory(), directory_name)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created")
    else:
        print(f"Directory '{directory_path}' exists")
    return directory_path
