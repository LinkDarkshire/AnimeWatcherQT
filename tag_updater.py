import requests
from bs4 import BeautifulSoup
import json
from PySide6.QtCore import QObject, Signal, QThread
import time

class TagListUpdater(QObject):
    finished = Signal()
    progress = Signal(int)
    total_pages_found = Signal(int)
    status = Signal(str)  # Neues Signal für Statusmeldungen

    def __init__(self, logger=None):
        super().__init__()
        self.tags = []
        self.page = 0
        self.total_pages = 0
        self.logger = logger
        self._processing = False

    def get_total_pages(self):
        page = 0
        while True:
            try:
                url = f"https://anidb.net/tag/?noalias=1&orderby.name=0.1&page={page}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                }
       
                print(f"Checking page {page} for content")
                response = requests.get(url, headers=headers)
                response.raise_for_status()
       
                soup = BeautifulSoup(response.content, "html.parser")
            
                no_results = soup.select("html body#anidb.taglist div#layout-content div#layout-main div.g_content.taglist_all div.g_section.g_datatable.taglist_list div.g_bubblewrap.nowrap div.g_msg.g_bubble.note div.container")
            
                print(f"Found {len(no_results)} no_results elements")
                if no_results:
                    for i, result in enumerate(no_results):
                        print(f"Element {i} text: [{result.text}]")
                        if "No results were found." in result.text:
                            print(f"Found last page: {page-1}")
                            return max(0, page - 1)  # Mindestens 0 zurückgeben
            
                print("-" * 50)
                time.sleep(1)
                page += 1
            
            except Exception as e:
                error_msg = f"Error checking page {page}: {str(e)}"
                print(error_msg)
                return -1  # Fehlerfall gibt -1 zurück

    def get_tags(self, page):
        url = f"https://anidb.net/tag/?noalias=1&orderby.name=0.1&page={page}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        try:
            self.logger.debug(f"Fetching tags from page {page}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            tag_list = soup.select("html body#anidb.taglist div#layout-content div#layout-main div.g_content.taglist_all div.g_section.g_datatable.taglist_list div.g_bubblewrap.nowrap table.g_section.taglist tbody tr.g_odd td.name.main.tag a")
            
            tags = []
            for tag in tag_list:
                tag_id = tag["href"].split("/")[-1]
                tag_name = tag.text.strip()
                tags.append({"id": tag_id, "name": tag_name})
            
            self.logger.debug(f"Found {len(tags)} tags on page {page}")
            return tags
            
        except Exception as e:
            error_msg = f"Error processing tags on page {page}: {str(e)}"
            self.logger.error(error_msg)
            self.status.emit(error_msg)
            return []

    def run(self):
        """Hauptmethode für den Thread"""
        self.logger.info("Tag updater thread started")
        self.status.emit("Starting tag update process")
        
        try:
            self._processing = True
            
            # Ermittle zunächst die Gesamtanzahl der Seiten
            self.status.emit("Determining total number of pages...")
            self.total_pages = self.get_total_pages()
            
            if self.total_pages < 0:  # Jetzt ist < 0 eindeutig ein Fehler
                error_msg = "Could not determine total pages"
                self.logger.error(error_msg)
                self.status.emit(error_msg)
                return
            
            self.logger.info(f"Found total pages: {self.total_pages}")
            self.total_pages_found.emit(self.total_pages)
            self.status.emit(f"Found {self.total_pages} pages to process")
            
            # Sammle Tags von jeder Seite
            for page in range(self.total_pages + 1):
                if not self._processing:
                    self.logger.info("Processing cancelled")
                    break
                
                self.status.emit(f"Processing page {page} of {self.total_pages}")
                self.progress.emit(page)
                
                page_tags = self.get_tags(page)
                if page_tags:
                    self.tags.extend(page_tags)
                    self.logger.debug(f"Total tags collected: {len(self.tags)}")
                
                time.sleep(1)  # Warte zwischen den Anfragen
            
            # Speichere Ergebnisse
            if self.tags:
                self.status.emit("Saving tags to file...")
                self.save_tags_to_json()
                self.status.emit("Tags saved successfully")
                
        except Exception as e:
            error_msg = f"Error in tag update process: {str(e)}"
            self.logger.error(error_msg)
            self.status.emit(error_msg)
        finally:
            self._processing = False
            self.logger.info("Tag updater finished")
            self.status.emit("Update process finished")
            self.finished.emit()

    def save_tags_to_json(self):
        try:
            if not self.tags:
                self.logger.warning("No tags to save")
                return
                
            with open("tags.json", "w", encoding='utf-8') as f:
                json.dump(self.tags, f, indent=4, ensure_ascii=False)
            self.logger.info(f"Successfully saved {len(self.tags)} tags to tags.json")
        except Exception as e:
            error_msg = f"Error saving tags to JSON: {str(e)}"
            self.logger.error(error_msg)
            self.status.emit(error_msg)