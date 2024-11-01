import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import os

class NFOParser:
    """
    Parser for NFO files containing AniDB IDs.

    This class handles the parsing of NFO files typically found in media collections
    to extract AniDB IDs used for anime identification.

    Attributes
    ----------
    nfo_filename : str
        The default filename to look for (typically 'tvshow.nfo')
    logger : logging.Logger
        Logger instance for tracking operations
    """

    def __init__(self, logger=None):
        """
        Initialize the NFO parser.

        Parameters
        ----------
        logger : logging.Logger
            Logger instance for tracking operations
        """
        self.nfo_filename = "tvshow.nfo"
        self.logger = logger
        self.logger.info("Initializing NFO Parser")
        self.logger.debug(f"Using default NFO filename: {self.nfo_filename}")

    def check_and_parse_nfo(self, folder_path: str) -> Optional[str]:
        """
        Check for existence of NFO file and extract AniDB ID if present.

        Parameters
        ----------
        folder_path : str
            Path to the folder containing the NFO file

        Returns
        -------
        Optional[str]
            The AniDB ID if found, None otherwise

        Notes
        -----
        The method looks for a specific XML element structure:
        <uniqueid type="anidb">12345</uniqueid>
        """
        self.logger.info(f"Checking for NFO file in: {folder_path}")

        try:
            # Convert to Path object and resolve any symlinks
            folder_path = Path(folder_path).resolve()
            nfo_path = folder_path / self.nfo_filename

            # Validate path
            if not folder_path.exists():
                self.logger.error(f"Folder does not exist: {folder_path}")
                return None

            if not folder_path.is_dir():
                self.logger.error(f"Path is not a directory: {folder_path}")
                return None

            # Check NFO existence
            if not nfo_path.exists():
                self.logger.debug(f"No NFO file found at: {nfo_path}")
                return None

            if not nfo_path.is_file():
                self.logger.error(f"NFO path exists but is not a file: {nfo_path}")
                return None

            # Check file size
            file_size = os.path.getsize(nfo_path)
            if file_size == 0:
                self.logger.warning(f"NFO file is empty: {nfo_path}")
                return None
            self.logger.debug(f"NFO file size: {file_size} bytes")

            # Read and parse XML
            self.logger.debug("Parsing NFO file")
            tree = ET.parse(nfo_path)
            root = tree.getroot()

            # Log root tag for debugging
            self.logger.debug(f"NFO root element: {root.tag}")

            # Search for AniDB ID
            for uniqueid in root.findall('.//uniqueid'):
                id_type = uniqueid.get('type', '').lower()
                self.logger.debug(f"Found uniqueid element with type: {id_type}")

                if id_type == 'anidb':
                    anidb_id = uniqueid.text.strip() if uniqueid.text else None

                    if not anidb_id:
                        self.logger.warning("Found anidb uniqueid element but it's empty")
                        continue

                    if not anidb_id.isdigit():
                        self.logger.warning(f"Found invalid AniDB ID (non-numeric): {anidb_id}")
                        continue

                    self.logger.info(f"Successfully extracted AniDB ID: {anidb_id}")
                    return anidb_id

            self.logger.info("No valid AniDB ID found in NFO file")
            return None

        except ET.ParseError as e:
            self.logger.error(f"XML parsing error in NFO file: {str(e)}")
            self.logger.debug(f"Parse error details - line: {e.position[0]}, column: {e.position[1]}")
            return None

        except FileNotFoundError as e:
            self.logger.error(f"NFO file not found: {str(e)}")
            return None

        except PermissionError as e:
            self.logger.error(f"Permission denied accessing NFO file: {str(e)}")
            return None

        except Exception as e:
            self.logger.error(f"Unexpected error parsing NFO file: {str(e)}")
            return None

    def validate_nfo_format(self, nfo_path: Path) -> bool:
        """
        Validate the basic structure of an NFO file.

        Parameters
        ----------
        nfo_path : Path
            Path to the NFO file to validate

        Returns
        -------
        bool
            True if the file has valid XML structure, False otherwise
        """
        self.logger.debug(f"Validating NFO file format: {nfo_path}")

        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()

            # Check for basic expected structure
            has_uniqueid = len(root.findall('.//uniqueid')) > 0

            if has_uniqueid:
                self.logger.debug("NFO file has valid structure with uniqueid elements")
                return True
            else:
                self.logger.warning("NFO file is valid XML but missing uniqueid elements")
                return False

        except ET.ParseError as e:
            self.logger.error(f"NFO file has invalid XML format: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error validating NFO format: {str(e)}")
            return False

    def get_all_ids(self, nfo_path: Path) -> dict:
        """
        Extract all uniqueid elements and their types from an NFO file.

        Parameters
        ----------
        nfo_path : Path
            Path to the NFO file

        Returns
        -------
        dict
            Dictionary of ID types and their values
        """
        self.logger.debug(f"Extracting all IDs from NFO file: {nfo_path}")

        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()

            ids = {}
            for uniqueid in root.findall('.//uniqueid'):
                id_type = uniqueid.get('type', '').lower()
                id_value = uniqueid.text.strip() if uniqueid.text else None

                if id_value:
                    ids[id_type] = id_value
                    self.logger.debug(f"Found ID - type: {id_type}, value: {id_value}")

            self.logger.info(f"Extracted {len(ids)} unique IDs from NFO file")
            return ids

        except Exception as e:
            self.logger.error(f"Error extracting IDs from NFO file: {str(e)}")
            return {}
