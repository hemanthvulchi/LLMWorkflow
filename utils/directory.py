import os

def get_current_directory():
    return os.getcwd()

def get_db_filepath(persist_directory):
    return os.path.join(persist_directory, "chroma.sqlite3") 

def open_document_directory():
    directory_path = check_directory('Documents')
    os.startfile(directory_path)

def check_documents_directory():
    return check_directory('documents')

def get_icon_path(file_name):
    complete_file_name = file_name + ".svg"
    current_directory = os.path.join(get_current_directory(), "resources\\node_icons")
    file_path = os.path.join(current_directory, complete_file_name)
    return file_path

def check_directory(directory_name):
    directory_path = os.path.join(get_current_directory(), directory_name)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created")
    else:
        print(f"Directory '{directory_path}' exists")
    return directory_path



if __name__ == "__main__":
    path = get_icon_path('powerpoint')
    print(path)