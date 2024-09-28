import json
import os

class AnimeInfoManager:
    """
    A class to manage anime information stored in a JSON file.

    Attributes
    ----------
    folder_path : str
        The path to the folder where the JSON file is located.
    file_path : str
        The full path to the JSON file.

    Methods
    -------
    create_json(anime_info: dict)
        Creates a JSON file with the given anime information.

    read_json() -> dict
        Reads the JSON file and returns the anime information as a dictionary.

    check_file_existence() -> bool
        Checks if the JSON file exists. Returns True if it exists, False otherwise.

    check_data_integrity(anime_info: dict) -> bool
        Checks the integrity of the anime information. Returns True if the data is valid, False otherwise.
    """

    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.file_path = os.path.join(folder_path, "aniinfo.json")

    def create_json(self, anime_info):
        with open(self.file_path, 'w') as file:
            json.dump(anime_info, file, indent=4)

    def read_json(self):
        with open(self.file_path, 'r') as file:
            anime_info = json.load(file)
        return anime_info

    def check_file_existence(self):
        return os.path.exists(self.file_path)

    def check_data_integrity(self, anime_info):
        required_keys = ['aid', 'year', 'type', 'romaji', 'kanji', 'english', 'synonyms', 'episodes', 'ep_count', 'special_count', 'tag_name_list', 'tag_id_list', 'tag_weigth_list']
        for key in required_keys:
            if key not in anime_info:
                return False
            if anime_info[key] is None or anime_info[key] == '':
                return False
        return True

# Example usage:
folder_path = "/path/to/folder"
anime_info_manager = AnimeInfoManager(folder_path)

# Check if the file exists
if anime_info_manager.check_file_existence():
    print("The file exists.")

    # Read the JSON file
    anime_info_read = anime_info_manager.read_json()
    print("Read anime info:", anime_info_read)

    # Check data integrity
    if anime_info_manager.check_data_integrity(anime_info_read):
        print("Data integrity is valid.")
    else:
        print("Data integrity is not valid. Some data is missing or not filled.")
else:
    print("The file does not exist.")
