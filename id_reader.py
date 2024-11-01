import json
from typing import Dict, List, Optional
from pathlib import Path

class TagIDReader:
    """
    A class to read tag IDs from a JSON file and retrieve their corresponding names.

    Attributes
    ----------
    tag_id_name_dict : Dict[str, str]
        A dictionary mapping tag IDs to their names.
    logger : logging.Logger
        Logger instance for tracking operations.

    Methods
    -------
    load_tag_ids() -> Dict[str, str]
        Loads tag IDs from the JSON file and returns a dictionary mapping IDs to names.

    get_names_by_ids(tag_ids_string: str) -> List[str]
        Takes a string of comma-separated tag IDs and returns a list of their corresponding names.
    """

    def __init__(self, logger=None):
        """
        Initialize the TagIDReader.

        Parameters
        ----------
        logger : logging.Logger
            Logger instance for tracking operations
        """
        self.logger = logger
        self.logger.info("Initializing TagIDReader")
        self.tags_file = Path("tags.json")
        self.tag_id_name_dict: Dict[str, str] = {}

        try:
            self.tag_id_name_dict = self.load_tag_ids()
            self.logger.info(f"Successfully loaded {len(self.tag_id_name_dict)} tags")
        except Exception as e:
            self.logger.error(f"Failed to initialize TagIDReader: {str(e)}")
            raise

    def load_tag_ids(self) -> Dict[str, str]:
        """
        Load and parse the tags JSON file.

        Returns
        -------
        Dict[str, str]
            Dictionary mapping tag IDs to tag names

        Raises
        ------
        FileNotFoundError
            If the tags.json file doesn't exist
        json.JSONDecodeError
            If the JSON file is invalid
        """
        self.logger.debug(f"Loading tags from {self.tags_file}")

        if not self.tags_file.exists():
            self.logger.error(f"Tags file not found: {self.tags_file}")
            raise FileNotFoundError(f"Tags file not found: {self.tags_file}")

        try:
            with open(self.tags_file, "r", encoding='utf-8') as file:
                self.logger.debug("Reading tags.json file")
                data = json.load(file)

                # Validate data structure
                if not isinstance(data, list):
                    self.logger.error("Invalid tags file format: root element must be an array")
                    raise ValueError("Invalid tags file format: root element must be an array")

                # Create dictionary with validation
                tag_dict = {}
                for item in data:
                    if not isinstance(item, dict) or 'id' not in item or 'name' not in item:
                        self.logger.warning(f"Skipping invalid tag entry: {item}")
                        continue

                    tag_id = str(item['id'])  # Convert ID to string for consistency
                    tag_dict[tag_id] = item['name']

                self.logger.debug(f"Successfully loaded {len(tag_dict)} tags")
                return tag_dict

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in tags file: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error loading tags: {str(e)}")
            raise

    def get_names_by_ids(self, tag_ids_string: str) -> List[str]:
        """
        Convert a comma-separated string of tag IDs to their corresponding names.

        Parameters
        ----------
        tag_ids_string : str
            Comma-separated string of tag IDs

        Returns
        -------
        List[str]
            List of tag names corresponding to the provided IDs
        """
        self.logger.debug(f"Processing tag IDs: {tag_ids_string}")

        if not tag_ids_string:
            self.logger.warning("Empty tag_ids_string provided")
            return []

        try:
            # Split and clean tag IDs
            tag_id_list = [id.strip() for id in tag_ids_string.split(',') if id.strip()]
            self.logger.debug(f"Found {len(tag_id_list)} tag IDs to process")

            names = []
            missing_ids = []

            for tag_id in tag_id_list:
                if tag_id in self.tag_id_name_dict:
                    name = self.tag_id_name_dict[tag_id]
                    names.append(name)
                    self.logger.debug(f"Mapped tag ID {tag_id} to name: {name}")
                else:
                    self.logger.warning(f"Tag ID not found: {tag_id}")
                    missing_ids.append(tag_id)
                    names.append("")

            # Log summary
            if missing_ids:
                self.logger.warning(f"Missing tags: {', '.join(missing_ids)}")
            else:
                self.logger.info(f"Successfully mapped all {len(tag_id_list)} tag IDs")

            return names

        except Exception as e:
            self.logger.error(f"Error processing tag IDs: {str(e)}")
            return []

    def reload_tags(self) -> bool:
        """
        Reload the tags from the JSON file.

        Returns
        -------
        bool
            True if reload was successful, False otherwise
        """
        self.logger.info("Reloading tags from file")
        try:
            new_tags = self.load_tag_ids()
            self.tag_id_name_dict = new_tags
            self.logger.info(f"Successfully reloaded {len(new_tags)} tags")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload tags: {str(e)}")
            return False

    def get_tag_count(self) -> int:
        """
        Get the number of loaded tags.

        Returns
        -------
        int
            Number of tags in the dictionary
        """
        count = len(self.tag_id_name_dict)
        self.logger.debug(f"Current tag count: {count}")
        return count

    def get_tag_name(self, tag_id: str) -> Optional[str]:
        """
        Get a single tag name by ID.

        Parameters
        ----------
        tag_id : str
            The ID of the tag to look up

        Returns
        -------
        Optional[str]
            The tag name if found, None otherwise
        """
        name = self.tag_id_name_dict.get(tag_id)
        if name:
            self.logger.debug(f"Found tag name for ID {tag_id}: {name}")
        else:
            self.logger.debug(f"No tag name found for ID {tag_id}")
        return name
