from pathlib import Path
import configparser
import json

class ConfigManager:
    def __init__(self, logger):
        """
        Initialize ConfigManager.
        
        Parameters
        ----------
        logger : Logger
            Logger instance for tracking operations
        """
        self.logger = logger
        self.config = configparser.ConfigParser()
        self.config_file = Path('config.ini')
        self.logger.info("Initializing ConfigManager")
        self.load_config()

    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file)
                self.logger.info("Configuration loaded from file")
                self.logger.debug(f"Config file path: {self.config_file}")
            else:
                self.logger.info("No config file found, creating default configuration")
                self._create_default_config()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            raise

    def _create_default_config(self):
        """Create default configuration"""
        try:
            self.config['Path'] = {
                'hentaiPath': '',
                'database': 'hentai.db',
                'tags_file': 'tags.json'
            }

            self.config['AniDB'] = {
                'username': '',
                'password': '',
                'client': 'lewdwatcher',
                'clientver': '1',
                'server': 'api.anidb.net',
                'port': '9000',
                'max_retries': '3'
            }

            self.save_config()
            self.logger.info("Default configuration created")
        except Exception as e:
            self.logger.error(f"Error creating default config: {str(e)}")
            raise

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            self.logger.info("Configuration saved to file")
            self.logger.debug(f"Saved to: {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            raise

    def get_path(self, key):
        """
        Get path from config with error handling.
        
        Parameters
        ----------
        key : str
            Configuration key to retrieve
            
        Returns
        -------
        str or None
            Configuration value if found, None otherwise
        """
        try:
            value = self.config.get('Path', key)
            self.logger.debug(f"Retrieved path for key '{key}': {value}")
            return value
        except configparser.NoSectionError:
            self.logger.error("Path section missing in config")
            return None
        except configparser.NoOptionError:
            self.logger.error(f"No configuration found for key: {key}")
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving path: {str(e)}")
            return None

    def set_path(self, key, value):
        """
        Set path in config with error handling.
        
        Parameters
        ----------
        key : str
            Configuration key to set
        value : str
            Value to set
        """
        try:
            if 'Path' not in self.config:
                self.logger.debug("Creating Path section in config")
                self.config.add_section('Path')
            
            self.config.set('Path', key, value)
            self.save_config()
            self.logger.info(f"Path updated - key: {key}, value: {value}")
        except Exception as e:
            self.logger.error(f"Error setting path: {str(e)}")
            raise
    def get_anidb_credentials(self):
        """
        Get AniDB credentials as dictionary.
    
        Returns
        -------
        dict
            Dictionary containing username and password
            or None if not configured
        """
        try:
            if not self.config.has_section('AniDB'):
                self.logger.error("No AniDB section in config")
                return None
        
            username = self.config.get('AniDB', 'username')
            password = self.config.get('AniDB', 'password')
        
            if not username or not password:
                self.logger.error("Username or password not configured")
                return None
            
            credentials = {
                'username': username,
                'password': password
            }
        
            self.logger.debug(f"Retrieved credentials for username: {username}")
            return credentials
        
        except Exception as e:
            self.logger.error(f"Error retrieving AniDB credentials: {str(e)}")
            return None
        
    def get_anidb_settings(self) -> dict:
        """
        Get AniDB settings including credentials and connection settings.
    
        Returns
        -------
        dict
            Dictionary containing all AniDB settings
        """
        try:
            if not self.config.has_section('AniDB'):
                self.logger.error("No AniDB section in config")
                return None
            
            credentials = self.get_anidb_credentials()
            if not credentials:
                return None

            # Erweitere das credentials dictionary um zusätzliche Einstellungen
            settings = {
                **credentials,  # Username und Password
                'max_retries': self.config.getint('AniDB', 'max_retries', fallback=3)
            }
        
            self.logger.debug("Retrieved AniDB settings successfully")
            return settings
        
        except Exception as e:
            self.logger.error(f"Error retrieving AniDB settings: {str(e)}")
            return None

    def check_config_integrity(self):
        """
        Check if all required configuration sections and options are present.
        
        Returns
        -------
        bool
            True if configuration is valid, False otherwise
        """
        try:
            required_sections = {
                'AniDB': ['username', 'password','client','clientver','server','port','max_retries']
            }

            for section, options in required_sections.items():
                if not self.config.has_section(section):
                    self.logger.error(f"Missing required section: {section}")
                    return False
                    
                for option in options:
                    if not self.config.has_option(section, option):
                        self.logger.error(f"Missing required option '{option}' in section '{section}'")
                        return False

            self.logger.info("Configuration integrity check passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking config integrity: {str(e)}")
            return False