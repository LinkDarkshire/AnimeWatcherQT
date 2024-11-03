import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import json

class AnimeDatabase:
    """
    A class used to manage a database of anime information.

    Attributes
    ----------
    conn : sqlite3.Connection
        The connection to the SQLite database.
    cursor : sqlite3.Cursor
        The cursor object used to execute SQL queries.
    logger : logging.Logger
        Logger instance for tracking database operations.
    """

    def __init__(self, logger=None, db_path="anime.db" ):
        self.logger = logger
        self.db_path = db_path
        self.logger.info(f"Initializing database connection to {db_path}")

        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.logger.debug("Database connection established successfully")
            self.create_table()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def create_table(self):
        """Creates the necessary database tables if they don't exist."""
        self.logger.info("Creating/verifying database tables")

        create_table_queries = {
            'anime_info': """
            CREATE TABLE IF NOT EXISTS anime_info (
                aid INTEGER PRIMARY KEY,
                year TEXT,
                type TEXT,
                romaji TEXT,
                kanji TEXT,
                synonyms TEXT,
                episodes INTEGER,
                ep_count INTEGER,
                special_count INTEGER,
                tag_id_list TEXT,
                tag_weigth_list TEXT,
                path TEXT
            );""",
            'tags': """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE
            );""",
            'anime_tags': """
            CREATE TABLE IF NOT EXISTS anime_tags (
                anime_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (anime_id) REFERENCES anime_info(aid),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                PRIMARY KEY (anime_id, tag_id)
            );"""
        }

        try:
            for table_name, query in create_table_queries.items():
                self.logger.debug(f"Creating table {table_name} if not exists")
                self.cursor.execute(query)

            self.conn.commit()
            self.logger.info("Database tables created/verified successfully")

        except sqlite3.Error as e:
            self.logger.error(f"Error creating database tables: {str(e)}")
            self.logger.debug(f"Failed query: {query}")
            raise

    def add_anime(self, anime_info: Dict[str, Any], path: str) -> Optional[int]:
        """
        Adds or updates an anime entry in the database.

        Parameters
        ----------
        anime_info : Dict[str, Any]
            Dictionary containing anime information
        path : str
            File system path to the anime

        Returns
        -------
        Optional[int]
            The ID of the inserted/updated record, or None if operation failed
        """
        self.logger.info(f"Adding/updating anime: {anime_info.get('romaji', 'Unknown title')}")
        self.logger.debug(f"Anime data: {json.dumps(anime_info, ensure_ascii=False)}")

        add_anime_query = """
        INSERT INTO anime_info (
            aid, year, type, romaji, kanji, synonyms, episodes, ep_count,
            special_count, tag_id_list, tag_weigth_list, path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(aid) DO UPDATE SET
            year = excluded.year,
            type = excluded.type,
            romaji = excluded.romaji,
            kanji = excluded.kanji,
            synonyms = excluded.synonyms,
            episodes = excluded.episodes,
            ep_count = excluded.ep_count,
            special_count = excluded.special_count,
            tag_id_list = excluded.tag_id_list,
            tag_weigth_list = excluded.tag_weigth_list,
            path = excluded.path
        """

        try:
            self.cursor.execute(add_anime_query, (
                anime_info['aid'],
                anime_info['year'],
                anime_info['type'],
                anime_info['romaji'],
                anime_info['kanji'],
                anime_info['synonyms'],
                anime_info['episodes'],
                anime_info['ep_count'],
                anime_info['special_count'],
                anime_info['tag_id_list'],
                anime_info['tag_weigth_list'],
                path
            ))

            anime_id = self.cursor.lastrowid
            self.conn.commit()

            self.logger.info(f"Successfully added/updated anime with ID {anime_info['aid']}")
            self.logger.debug(f"Database record ID: {anime_id}")

            return anime_id

        except sqlite3.Error as e:
            self.logger.error(f"Database error while adding anime: {str(e)}")
            self.logger.debug("Rolling back transaction")
            self.conn.rollback()
            return None
        except KeyError as e:
            self.logger.error(f"Missing required field in anime_info: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error while adding anime: {str(e)}")
            return None

    def add_tags_and_link_to_anime(self, anime_id: int, tag_names: List[str]) -> bool:
        """
        Adds tags to the database and links them to the specified anime.

        Parameters
        ----------
        anime_id : int
            The ID of the anime to link tags to
        tag_names : List[str]
            List of tag names to add and link

        Returns
        -------
        bool
            True if operation was successful, False otherwise
        """
        self.logger.info(f"Adding and linking tags for anime ID {anime_id}")
        self.logger.debug(f"Tags to process: {tag_names}")

        try:
            for tag_name in tag_names:
                # Add tag if not exists
                self.logger.debug(f"Processing tag: {tag_name}")

                self.cursor.execute(
                    "INSERT INTO tags (tag_name) VALUES (?) ON CONFLICT(tag_name) DO NOTHING",
                    (tag_name,)
                )

                # Get tag ID
                self.cursor.execute("SELECT id FROM tags WHERE tag_name = ?", (tag_name,))
                tag_id = self.cursor.fetchone()[0]

                # Link tag to anime
                self.cursor.execute(
                    "INSERT INTO anime_tags (anime_id, tag_id) VALUES (?, ?)",
                    (anime_id, tag_id)
                )

                self.logger.debug(f"Tag {tag_name} (ID: {tag_id}) linked to anime {anime_id}")

            self.conn.commit()
            self.logger.info(f"Successfully processed {len(tag_names)} tags for anime {anime_id}")
            return True

        except sqlite3.Error as e:
            self.logger.error(f"Database error while processing tags: {str(e)}")
            self.conn.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error while processing tags: {str(e)}")
            return False

    def anime_exists(self, romaji: str) -> bool:
        """
        Checks if an anime with the given romaji name exists in the database.

        Parameters
        ----------
        romaji : str
            The romaji name to check

        Returns
        -------
        bool
            True if anime exists, False otherwise
        """
        self.logger.debug(f"Checking if anime exists: {romaji}")

        try:
            self.cursor.execute(
                "SELECT 1 FROM anime_info WHERE romaji = ? LIMIT 1",
                (romaji,)
            )
            exists = self.cursor.fetchone() is not None

            self.logger.debug(f"Anime '{romaji}' {'exists' if exists else 'does not exist'}")
            return exists

        except sqlite3.Error as e:
            self.logger.error(f"Database error while checking anime existence: {str(e)}")
            return False

    def get_anime_list(self) -> List[tuple]:
        """
        Retrieves a list of all anime in the database.

        Returns
        -------
        List[tuple]
            List of tuples containing anime information
        """
        self.logger.info("Retrieving complete anime list")

        try:
            self.cursor.execute("SELECT * FROM anime_info")
            results = self.cursor.fetchall()

            self.logger.info(f"Retrieved {len(results)} anime records")
            self.logger.debug("Anime list retrieval successful")
            return results

        except sqlite3.Error as e:
            self.logger.error(f"Database error while retrieving anime list: {str(e)}")
            return []
        
    def clean_database(self, existing_paths: List[str] = None) -> Tuple[int, List[str]]:
        """
        Clean the database by removing entries with non-existing paths or all entries if no paths provided.
        
        Parameters
        ----------
        existing_paths : List[str], optional
            List of valid paths to keep. If None, removes all entries.
            
        Returns
        -------
        Tuple[int, List[str]]
            Number of deleted entries and list of removed anime names
        """
        try:
            self.logger.info("Starting database cleanup")
            deleted_count = 0
            removed_anime = []

            if existing_paths is None:
                # Delete all entries
                self.logger.info("Removing all entries from database")
                self.cursor.execute("SELECT romaji, path FROM anime_info")
                all_entries = self.cursor.fetchall()
                
                self.cursor.execute("DELETE FROM anime_info")
                deleted_count = len(all_entries)
                removed_anime = [entry[0] for entry in all_entries]
                
            else:
                # Convert paths to set for faster lookup
                valid_paths = set(str(Path(p).resolve()) for p in existing_paths)
                
                # Get entries with invalid paths
                self.cursor.execute("SELECT aid, romaji, path FROM anime_info")
                entries = self.cursor.fetchall()
                
                for aid, romaji, path in entries:
                    if not path or str(Path(path).resolve()) not in valid_paths:
                        self.cursor.execute("DELETE FROM anime_info WHERE aid = ?", (aid,))
                        deleted_count += 1
                        removed_anime.append(romaji)
                        self.logger.debug(f"Removed entry for {romaji} with invalid path: {path}")

            self.conn.commit()
            self.logger.info(f"Database cleanup completed: removed {deleted_count} entries")
            return deleted_count, removed_anime
            
        except sqlite3.Error as e:
            self.logger.error(f"Database error during cleanup: {str(e)}")
            self.conn.rollback()
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during database cleanup: {str(e)}")
            self.conn.rollback()
            raise

    def close(self):
        """Closes the database connection."""
        self.logger.info("Closing database connection")

        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.commit()
                self.conn.close()
            self.logger.debug("Database connection closed successfully")

        except sqlite3.Error as e:
            self.logger.error(f"Error while closing database connection: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error while closing database: {str(e)}")

    def __del__(self):
        """Destructor to ensure database connection is closed."""
        self.logger.debug("Database object being destroyed")
        try:
            self.close()
        except Exception as e:
            self.logger.error(f"Error in destructor: {str(e)}")
