import json

class TagIDReader:
    """
    A class to read tag IDs from a JSON file and retrieve their corresponding names.

    Attributes
    ----------
    tag_id_name_dict : dict
        A dictionary mapping tag IDs to their names.

    Methods
    -------
    __init__()
        Initializes the TagIDReader by loading the tag IDs from the JSON file.

    load_tag_ids() -> dict
        Loads tag IDs from the JSON file and returns a dictionary mapping IDs to names.

    get_names_by_ids(tag_ids_string: list) -> list
        Takes a list of tag IDs as a string, splits them, and returns a list of their corresponding names.
        If a tag ID is not found in the dictionary, an empty string is appended to the list.
    """

    def __init__(self: str):
        self.tag_id_name_dict = self.load_tag_ids()

    def load_tag_ids(self: str) -> dict:
        with open("tags.json", "r") as file:
            data = json.load(file)
            tag_id_name_dict = {item['id']: item['name'] for item in data}
        return tag_id_name_dict

    def get_names_by_ids(self, tag_ids_string: list) -> list:
        tag_id_list = tag_ids_string.split(',')
        names = []
        for id in tag_id_list:
            if id in self.tag_id_name_dict:
                names.append(self.tag_id_name_dict[id])
            else:
                print(f"ID '{id}' nicht gefunden.")  # Debugging-Output
                names.append("")

        return names
