import json
import os

def dir_exists(directory):
    return os.path.isdir(directory)

def get_json_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def make_directory_if_not_exists(directory):
    os.makedirs(os.path.dirname(directory), exist_ok=True)