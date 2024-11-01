from pathlib import Path
import configparser
import json

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = Path('config.ini')
        self.load_config()

    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration"""
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
            'port': '9000'
        }

        self.save_config()

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_path(self, key):
        """Get path from config with error handling"""
        try:
            return self.config.get('Path', key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None

    def set_path(self, key, value):
        """Set path in config with error handling"""
        if 'Path' not in self.config:
            self.config.add_section('Path')
        self.config.set('Path', key, value)
        self.save_config()

    def get_anidb_credentials(self):
        """
        Get AniDB credentials as dictionary.
        
        Returns
        -------
        dict
            Dictionary containing username, password, client and clientver
            or None if not configured
        """
        try:
            if not self.config.has_section('AniDB'):
                self.logger.error("No AniDB section in config")
                return None
                
            # Direkt als Dictionary zurückgeben
            return {
                'username': self.config.get('AniDB', 'username'),
                'password': self.config.get('AniDB', 'password')
            }
        except Exception as e:
            self.logger.error(f"Error getting AniDB credentials: {str(e)}")
            return None
