import json
from pathlib import Path
from typing import Dict, Any, Optional

class AnimeInfoManager:
    """
    A class to manage anime information stored in a JSON file.

    Attributes
    ----------
    folder_path : Path
        The path to the folder where the JSON file is located.
    file_path : Path
        The full path to the JSON file.
    logger : logging.Logger
        Logger instance for tracking operations
    """

    def __init__(self, folder_path: str, logger=None):
        """
        Initialize the AnimeInfoManager.

        Parameters
        ----------
        folder_path : str
            Path to the folder where the JSON file should be stored
        logger : logging.Logger
            Logger instance for tracking operations
        """
        self.logger = logger
        self.folder_path = Path(folder_path)
        self.file_path = self.folder_path / "aniinfo.json"
        self.logger.info(f"Initialized AnimeInfoManager for path: {self.folder_path}")
        self.logger.debug(f"JSON file path: {self.file_path}")

    def create_json(self, anime_info: Dict[str, Any]) -> bool:
        """
        Creates a JSON file with the given anime information.

        Parameters
        ----------
        anime_info : Dict[str, Any]
            Dictionary containing anime information to be saved

        Returns
        -------
        bool
            True if successful, False otherwise
        """
        self.logger.info(f"Creating JSON file for anime: {anime_info.get('romaji', 'Unknown')}")
        
        try:
            # Ensure the directory exists
            self.folder_path.mkdir(parents=True, exist_ok=True)
            
            # Validate data before writing
            if not self.check_data_integrity(anime_info):
                self.logger.error("Data integrity check failed, aborting JSON creation")
                return False

            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(anime_info, file, indent=4, ensure_ascii=False)
                
            self.logger.info("JSON file created successfully")
            self.logger.debug(f"Written to: {self.file_path}")
            return True

        except PermissionError as e:
            self.logger.error(f"Permission denied writing JSON file: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"Error encoding JSON data: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating JSON file: {str(e)}")
            return False

    def read_json(self) -> Optional[Dict[str, Any]]:
        """
        Reads the JSON file and returns the anime information.

        Returns
        -------
        Optional[Dict[str, Any]]
            Dictionary containing anime information or None if reading fails
        """
        self.logger.info(f"Reading JSON file from: {self.file_path}")
        
        if not self.check_file_existence():
            self.logger.warning("JSON file does not exist")
            return None

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                anime_info = json.load(file)
                
            if self.check_data_integrity(anime_info):
                self.logger.info("Successfully read and validated JSON data")
                self.logger.debug(f"Read data for anime: {anime_info.get('romaji', 'Unknown')}")
                return anime_info
            else:
                self.logger.error("Read JSON data failed integrity check")
                return None

        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON file: {str(e)}")
            return None
        except PermissionError as e:
            self.logger.error(f"Permission denied reading JSON file: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error reading JSON file: {str(e)}")
            return None

    def check_file_existence(self) -> bool:
        """
        Checks if the JSON file exists.

        Returns
        -------
        bool
            True if file exists, False otherwise
        """
        exists = self.file_path.exists()
        self.logger.debug(f"File existence check: {exists} for {self.file_path}")
        return exists

    def check_data_integrity(self, anime_info: Dict[str, Any]) -> bool:
        """
        Checks the integrity of the anime information.

        Parameters
        ----------
        anime_info : Dict[str, Any]
            Dictionary containing anime information to validate

        Returns
        -------
        bool
            True if data is valid, False otherwise
        """
        self.logger.debug("Checking data integrity")
        
        required_keys = [
            'aid', 'year', 'type', 'romaji', 'kanji', 'english', 'synonyms',
            'episodes', 'ep_count', 'special_count', 'tag_name_list',
            'tag_id_list', 'tag_weigth_list'
        ]

        try:
            # Check if all required keys exist
            missing_keys = [key for key in required_keys if key not in anime_info]
            if missing_keys:
                self.logger.warning(f"Missing required keys: {', '.join(missing_keys)}")
                return False

            # Check for empty or None values
            empty_keys = [
                key for key in required_keys 
                if anime_info[key] is None or anime_info[key] == ''
            ]
            if empty_keys:
                self.logger.warning(f"Empty values for keys: {', '.join(empty_keys)}")
                return False

            self.logger.debug("Data integrity check passed")
            return True

        except Exception as e:
            self.logger.error(f"Error during data integrity check: {str(e)}")
            return False

    def validate_json_structure(self) -> bool:
        """
        Validates the structure of the existing JSON file.

        Returns
        -------
        bool
            True if file has valid structure, False otherwise
        """
        self.logger.info("Validating JSON file structure")
        
        try:
            if not self.check_file_existence():
                self.logger.warning("Cannot validate non-existent file")
                return False

            anime_info = self.read_json()
            if anime_info is None:
                return False

            return self.check_data_integrity(anime_info)

        except Exception as e:
            self.logger.error(f"Error validating JSON structure: {str(e)}")
            return False

    def backup_json(self) -> bool:
        """
        Creates a backup of the JSON file if it exists.

        Returns
        -------
        bool
            True if backup was successful or not needed, False if backup failed
        """
        if not self.check_file_existence():
            self.logger.debug("No file to backup")
            return True

        try:
            backup_path = self.file_path.with_suffix('.json.bak')
            self.file_path.rename(backup_path)
            self.logger.info(f"Created backup at: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")
            return False