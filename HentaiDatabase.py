import sqlite3

class HentaiDatabase:
    """
    A class used to manage a database of hentai anime information.

    Attributes
    ----------
    conn : sqlite3.Connection
        The connection to the SQLite database.
    cursor : sqlite3.Cursor
        The cursor object used to execute SQL queries.

    Methods
    -------
    __init__(self, db_path="hentai.db")
        Initializes the HentaiDatabase object and creates the necessary tables.

    create_table(self)
        Creates the "hentai_info" table in the database.

    add_anime(self, anime_info, path)
        Adds a new anime to the database or updates existing anime information.

    add_tags_and_link_to_hentai(self, hentai_id, tag_names)
        Adds tags to the database and links them to the specified anime.

    anime_exists(self, romaji)
        Checks if an anime with the given romaji exists in the database.

    get_anime_list(self)
        Retrieves a list of all anime in the database.

    close(self)
        Closes the database connection.
    """

    def __init__(self, db_path="hentai.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Create the "hentai_info" table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS hentai_info (
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
        );
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def add_anime(self, anime_info, path):
        add_anime_query = """
        INSERT INTO hentai_info (
            aid, year, type, romaji, kanji, synonyms, episodes, ep_count, special_count, tag_id_list, tag_weigth_list, path
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        ) ON CONFLICT(aid) DO UPDATE SET
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
        hentai_id = self.cursor.lastrowid

        # Add tags if not already present and link them to the anime
        # self.add_tags_and_link_to_hentai(hentai_id, anime_info['tag_id_list'].split(','))

        self.conn.commit()

    def add_tags_and_link_to_hentai(self, hentai_id, tag_names):
        # Add tags if not already present
        add_tags_query = "INSERT INTO tags (tag_name) VALUES (?) ON CONFLICT(tag_name) DO NOTHING"
        link_tags_query = "INSERT INTO hentai_tags (hentai_id, tag_id) VALUES (?, ?)"
        for tag_name in tag_names:
            self.cursor.execute(add_tags_query, (tag_name, 1))  # Assigning a default weight of 1, adjust as needed
            self.cursor.execute("SELECT id FROM tags WHERE tag_name = ?", (tag_name,))
            tag_id = self.cursor.fetchone()[0]
            self.cursor.execute(link_tags_query, (hentai_id, tag_id))
        self.conn.commit()

    def anime_exists(self, romaji):
        query = "SELECT 1 FROM hentai_info WHERE romaji = ? LIMIT 1"
        self.cursor.execute(query, (romaji,))
        return self.cursor.fetchone() is not None

    def get_anime_list(self):
        get_anime_list_query = "SELECT * FROM anime_info;"
        self.cursor.execute(get_anime_list_query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()
