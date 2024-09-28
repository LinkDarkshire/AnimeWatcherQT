import requests
from bs4 import BeautifulSoup
import json
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class TagListUpdater(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.tags = []
        self.page = 0

    def get_tags(self, page):
        """
        Fetch a list of tags from AniDB's tag page.

        Parameters:
        page (int): The page number to fetch tags from.

        Returns:
        list: A list of dictionaries, where each dictionary represents a tag with 'id' and 'name' keys.
        """
        url = f"https://anidb.net/tag/?noalias=1&orderby.name=0.1&page={page}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        tag_list = soup.select("html body#anidb.taglist div#layout-content div#layout-main div.g_content.taglist_all div.g_section.g_datatable.taglist_list div.g_bubblewrap.nowrap table.g_section.taglist tbody tr.g_odd td.name.main.tag a")
        tags = []

        for tag in tag_list:
            tag_id = tag["href"].split("/")[-1]
            tag_name = tag.text.strip()
            tags.append({"id": tag_id, "name": tag_name})

        return tags

    def update_tags_json(self):
        # Starte den asynchronen Prozess für das Abrufen der Tags
        self.fetch_next_page()

    def fetch_next_page(self):
        print(f"Fetching tags from page {self.page}")
        self.progress.emit(self.page)  # Fortschritt signalisieren
        page_tags = self.get_tags(self.page)

        if not page_tags:
            # Keine weiteren Tags, Prozess beenden und Datei schreiben
            self.save_tags_to_json()
            self.finished.emit()  # Prozess beendet
            return

        self.tags.extend(page_tags)
        self.page += 1

        # Füge eine Verzögerung hinzu, bevor die nächste Seite geladen wird
        QTimer.singleShot(1000, self.fetch_next_page)  # 1 Sekunde warten, dann nächste Seite

    def save_tags_to_json(self):
        # Speichere die Tags in eine JSON-Datei
        with open("tags.json", "w") as f:
            json.dump(self.tags, f, indent=4)
