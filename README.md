# Lewd Watcher

A Python-based desktop application for managing anime collections using the AniDB UDP API. The application helps organize your anime collection by fetching metadata from AniDB and maintaining a local database.

## Features

### Directory Scanner

- Recursive scanning of folder structures
- Anime file detection
- Filename and format validation

### Metadata Management

- AniDB API integration
- Web scraping for tag information
- Local JSON storage per anime
- Central database integration

### Episode Tracking

- Automatic detection of existing episodes in EXX format (e.g., E01, E02)
- Missing episode identification through comparison with total count
- Overview display of missing episodes (e.g., "Episodes 4-12 missing")
- Collection status monitoring per anime
- Automatic updates when adding new episodes

### Episode Management

- Standardized episode file naming in "EXX" format
- Optional automatic renaming of non-standard files
- Season-based episode grouping
- Status tracking (available/missing) per episode
- Notifications for newly available episodes

## Prerequisites

- Python 3.8 or higher
- PySide6 (Qt for Python)
- AniDB Account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lewd-watcher.git
cd lewd-watcher
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create the UI file from the designer file:
```bash
pyside6-uic form.ui -o ui_form.py
```

## Configuration

1. Create a `config.ini` file in the root directory or run the application to generate a default one:

```ini
[AniDB]
username = your_username
password = your_password
client = lewdwatcher
clientver = 1
server = api.anidb.net
port = 9000
max_retries = 3

[Path]
hentaipath = /path/to/your/anime/collection
```

2. Make sure your AniDB account is activated and you have accepted their terms of service.

## Usage

1. Start the application:
```bash
python main.py
```

2. Select your anime collection folder using the "Search Folder" button.
3. Click "Update Tags" to synchronize the tag database with AniDB.
4. Use "Get Hentais" to scan your collection and fetch metadata.
5. The application will:
   - Check for existing NFO files
   - Query AniDB for metadata
   - Create JSON metadata files
   - Update the local database
   - Display progress in the UI

## Features in Detail

### NFO Support
- Automatically reads existing NFO files for AniDB IDs
- Compatible with popular media center software

### Metadata Management
- Stores detailed anime information in JSON format
- Includes titles, episode counts, tags, and more
- Maintains a local SQLite database for quick access

### Tag System
- Synchronizes with AniDB's tag database
- Provides local caching of tags
- Supports tag mapping and searching

### Error Handling
- Configurable retry mechanism for API timeouts
- Rate limiting compliance
- Detailed logging system

## Development

The project uses:
- PySide6 for the GUI
- SQLite for the database
- AniDB's UDP API for metadata
- Async/await for API communication
- Python's logging system for debugging

### Project Structure
```
lewd-watcher/
├── main.py
├── async_client.py
├── config_manager.py
├── database.py
├── json_handler.py
├── logger.py
├── nfo_parser.py
├── tag_updater.py
├── widget.py
├── form.ui
└── requirements.txt
```

## API Compliance

This application follows AniDB's API guidelines:
- Implements proper rate limiting
- Handles ban scenarios
- Respects API version requirements
- Uses appropriate client identification

## ToDo

1. by converting to asyncron I seem to have destroyed the infoFile storage -> wip
2. the tags list is not complete the whole categories are missing -> sort out or ignore ?
3. the missing number of episodes is still missing
4. saving Infos in DB not working at the moment
5. Stop search by user

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AniDB for providing the API
- Qt for the GUI framework
- The anime community

## Disclaimer

This application is not officially affiliated with AniDB. Please ensure you comply with AniDB's terms of service and API usage guidelines.

## Support

For issues and feature requests, please use the GitHub issue tracker.

---

**Note**: This application uses the AniDB UDP API. Please be mindful of their [API usage guidelines](https://wiki.anidb.net/UDP_API_Definition) to avoid getting banned.
