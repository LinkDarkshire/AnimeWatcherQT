# This Python file uses the following encoding: utf-8
import sys
import os
import asyncio
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PySide6.QtCore import QThread, QTimer, Signal
from pathlib import Path
from async_client import AsyncAniDBClient
from database import AnimeDatabase
from json_handler import AnimeInfoManager
from tag_updater import TagListUpdater
from id_reader import TagIDReader
from nfo_parser import NFOParser
from logger import AppLogger
from config_manager import ConfigManager

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget

class AnimeProcessingWorker(QThread):
    anime_processed = Signal(dict)  # Signal für verarbeiteten Anime
    error_occurred = Signal(str)    # Signal für Fehler
    processing_finished = Signal(bool)  # Neues Signal mit cancelled Status

    def __init__(self, config, logger, folder_path):
        super().__init__()
        self.config = config
        self.logger = logger
        self.folder_path = folder_path
        self._should_cancel = False
        self._is_running = False

    def cancel(self):
        """Markiert den Worker zum Beenden"""
        self._should_cancel = True
        self.logger.info("Cancel requested")  

    async def process_single_anime(self, anime_name, full_path, db, aniDB_client, tagreader, nfo_parser):
        if self._should_cancel:
            self.logger.info(f"Skipping {anime_name} due to cancel request")
            return None
        try:
            self.logger.debug(f"Processing anime: {anime_name}")
            
            if not db.anime_exists(anime_name):
                self.logger.debug(f"Anime {anime_name} not in database, processing...")
                anidb_id = nfo_parser.check_and_parse_nfo(full_path)
                hson = AnimeInfoManager(full_path, logger=self.logger)
                
                anime_info = None
                if not hson.check_file_existence():
                    anime_info = await self.fetch_anime_info(
                        anime_name, 
                        anidb_id, 
                        aniDB_client
                    )
                    
                    if anime_info:
                        anime_info['tag_name_list'] = tagreader.get_names_by_ids(anime_info['tag_id_list'])
                        hson.create_json(anime_info)
                        db.add_anime(anime_info, full_path)
                        return anime_info
                else:
                    return await self.process_existing_json(
                        hson, 
                        db, 
                        full_path, 
                        anime_name, 
                        anidb_id, 
                        aniDB_client, 
                        tagreader
                    )
            else:
                self.logger.debug(f"Anime {anime_name} already in database")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing {anime_name}: {str(e)}")
            raise

    async def fetch_anime_info(self, anime_name: str, anidb_id: str, aniDB_client: AsyncAniDBClient):
        try:
            if anidb_id:
                self.logger.debug(f"Fetching anime info by ID: {anidb_id}")
                return await aniDB_client.query_anime(anidb_id, by_id=True)
            else:
                self.logger.debug(f"Fetching anime info by name: {anime_name}")
                return await aniDB_client.query_anime(anime_name)
        except Exception as e:
            self.logger.error(f"Error fetching anime info: {str(e)}")
            return None

    async def process_existing_json(self, hson, db, full_path, anime_name, anidb_id, 
                                  aniDB_client, tagreader):
        try:
            if hson.check_data_integrity():
                self.logger.debug(f"Reading existing JSON for {anime_name}")
                anime_info = hson.read_json()
                db.add_anime(anime_info, full_path)
                return anime_info
            else:
                self.logger.warning(f"Corrupted JSON for {anime_name}, refetching")
                anime_info = await self.fetch_anime_info(
                    anime_name, 
                    anidb_id, 
                    aniDB_client
                )
                if anime_info:
                    anime_info['tag_name_list'] = tagreader.get_names_by_ids(anime_info['tag_id_list'])
                    hson.create_json(anime_info)
                    db.add_anime(anime_info, full_path)
                    return anime_info
        except Exception as e:
            self.logger.error(f"Error processing JSON: {str(e)}")
            return None

    def run(self):
        self._is_running = True
        async def main():
            try:
                if self._should_cancel:
                    return
                
                db = AnimeDatabase(logger=self.logger)
                tagreader = TagIDReader(logger=self.logger)
                nfo_parser = NFOParser(logger=self.logger)

                settings = self.config.get_anidb_settings()
                if not settings:
                    raise ValueError("No AniDB settings configured")

                async with AsyncAniDBClient(
                    credentials={'username': settings['username'], 'password': settings['password']},
                    logger=self.logger,
                    max_retries=settings['max_retries']
                ) as aniDB_client:
                    for anime_name in os.listdir(self.folder_path):
                        if self._should_cancel:
                            self.logger.info("Processing cancelled by user")
                            return
                        
                        full_path = os.path.join(self.folder_path, anime_name)
                        if os.path.isdir(full_path):
                            anime_info = await self.process_single_anime(
                                anime_name,
                                full_path,
                                db,
                                aniDB_client,
                                tagreader,
                                nfo_parser
                            )
                            if anime_info:
                                self.anime_processed.emit(anime_info)

                

            except Exception as e:
                self.logger.error(f"Error in processing thread: {str(e)}")
                self.error_occurred.emit(str(e))
            finally:
                self._is_running = False
                # Emit finished signal before asyncio.run ends
                self.processing_finished.emit(self._should_cancel)

        try:
            asyncio.run(main())
        except Exception as e:
            self.logger.error(f"Error in asyncio.run: {str(e)}")
            self._is_running = False
            self.processing_finished.emit(self._should_cancel)

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize logger first
        self.logger = AppLogger()
        # Pass logger to ConfigManager
        self.config = ConfigManager(logger=self.logger)

        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.logger.info("Application started")
        self.initUI()

    def initUI(self):
        try:
            # Existierende Verbindungen
            self.ui.bSearchFolder.clicked.connect(self.selectFolder)
            self.ui.bUpdateTags.clicked.connect(self.update_tags)
            self.ui.bGetHentai.clicked.connect(self.processFolder)

            # Neue Clean-Button Verbindung
            self.ui.cleanButton.clicked.connect(self.clean_up)

            # Cancel-Button Connection
            self.ui.bCancel.clicked.connect(self.cancel_processing)

            # Initial verstecken
            self.ui.bCancel.setVisible(False)

            # Progress Bar initial setup
            self.ui.progressBar.setValue(0)
            self.ui.progressBar.setVisible(False)

            self.get_config_path()
            self.logger.debug("UI initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing UI: {str(e)}")
            self.ui.lOutput.setText("Error initializing application")

    def closeEvent(self, event):
        """Handle application closing"""
        if hasattr(self, 'worker') and self.worker._is_running:
            self.worker.cancel()
            self.worker.wait()  # Warte auf Thread-Beendigung
        event.accept()

    def selectFolder(self):
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
            if folder_path:
                self.ui.tPath.setText(folder_path)
                self.config.set_path('hentaiPath', folder_path)
                self.logger.info(f"Selected folder: {folder_path}")
        except Exception as e:
            self.logger.error(f"Error selecting folder: {str(e)}")
            self.ui.lOutput.setText("Error selecting folder")

    def processFolder(self):
        try:
            if hasattr(self, 'worker') and self.worker._is_running:
                self.logger.warning("Processing already running")
                return
            
            folder_path = self.ui.tPath.toPlainText()
            if not folder_path:
                self.logger.warning("No folder path selected")
                self.ui.lOutput.setText("Please select a folder first")
                return

            # Check credentials before starting
            if not self.config.check_config_integrity():
                self.logger.error("Invalid configuration")
                self.ui.lOutput.setText("Please configure AniDB credentials first")
                return

            self.logger.info(f"Processing folder: {folder_path}")

            # UI Update
            self.setUIEnabled(False)
            self.ui.bCancel.setVisible(True)
            self.ui.bCancel.setEnabled(True)
            self.ui.bCancel.setText("Cancel")
            self.ui.progressBar.setVisible(True)

            # Zähle zunächst die Gesamtanzahl der zu verarbeitenden Ordner
            total_folders = sum(1 for entry in os.scandir(folder_path) if entry.is_dir())
            if total_folders == 0:
                self.logger.warning("No subdirectories found")
                self.ui.lOutput.setText("No subdirectories found in selected folder")
                self.setUIEnabled(True)
                return

            self.ui.progressBar.setMaximum(total_folders)
        
            # Create and start worker thread
            self.worker = AnimeProcessingWorker(self.config, self.logger, folder_path)
            self.worker.anime_processed.connect(self.on_anime_processed)
            self.worker.error_occurred.connect(self.on_error_occurred)
            self.worker.processing_finished.connect(self.on_processing_finished)
            self.worker.start()

        except Exception as e:
            self.logger.error(f"Error setting up processing: {str(e)}")
            self.ui.lOutput.setText(f"Error: {str(e)}")
            self.setUIEnabled(True)

    def on_anime_processed(self, anime_info):
        """Handle processed anime information"""
        try:
            self.displayAnimeInfo(anime_info)
            current_progress = self.ui.progressBar.value() + 1
            self.ui.progressBar.setValue(current_progress)
        except Exception as e:
            self.logger.error(f"Error handling processed anime: {str(e)}")

    def on_error_occurred(self, error_message):
        """Handle processing errors"""
        self.logger.error(f"Processing error: {error_message}")
        self.ui.lOutput.setText(f"Error: {error_message}")
        self.setUIEnabled(True)

    def on_processing_finished(self, was_cancelled: bool):
        """Handle completion of processing"""
        try:
            if hasattr(self, 'worker'):
                if self.worker._is_running:
                    self.worker.wait()  # Warte auf Thread-Beendigung
                self.worker.deleteLater()
                delattr(self, 'worker')

            self.setUIEnabled(True)
            self.ui.bCancel.setVisible(False)
            
            if was_cancelled:
                self.ui.lOutput.setText("Processing cancelled")
            else:
                self.ui.lOutput.setText("Processing completed")
                
            QTimer.singleShot(2000, lambda: self.ui.progressBar.setVisible(False))
        except Exception as e:
            self.logger.error(f"Error in processing finished handler: {str(e)}")

    def displayAnimeInfo(self, anime_info):
        try:
            item_text = f"{anime_info['romaji']} - {anime_info['ep_count']} Episodes"
            self.ui.listHentai.addItem(item_text)
            self.logger.debug(f"Added anime to list: {item_text}")
        except Exception as e:
            self.logger.error(f"Error displaying anime info: {str(e)}")

    def update_tags(self):
        try:
            self.logger.info("Starting tag update")
            self.thread = QThread()
            self.updater = TagListUpdater(logger=self.logger)

            self.updater.finished.connect(self.on_update_finished)
            self.updater.moveToThread(self.thread)
            self.thread.started.connect(self.updater.update_tags_json)

            self.thread.start()
            self.ui.bUpdateTags.setEnabled(False)

        except Exception as e:
            self.logger.error(f"Error updating tags: {str(e)}")
            self.ui.lOutput.setText("Error updating tags")
            self.ui.bUpdateTags.setEnabled(True)

    def on_update_finished(self):
        try:
            self.thread.quit()
            self.thread.wait()

            self.updater.deleteLater()
            self.thread.deleteLater()

            self.ui.bUpdateTags.setEnabled(True)
            self.logger.info("Tag update completed")
            self.ui.lOutput.setText("Tags updated successfully")

        except Exception as e:
            self.logger.error(f"Error in update finished: {str(e)}")
            self.ui.bUpdateTags.setEnabled(True)

    def get_config_path(self):
        try:
            path = self.config.get_path('hentaiPath')
            if path:
                self.ui.tPath.setText(path)
                self.logger.debug(f"Loaded path from config: {path}")
        except Exception as e:
            self.logger.error(f"Error reading config path: {str(e)}")

    def clean_up(self):
        """Remove all aniinfo.json files from subdirectories and clean the database."""
        try:
            folder_path = self.ui.tPath.toPlainText()
            if not folder_path:
                self.logger.warning("No folder path selected for cleaning")
                self.ui.lOutput.setText("Please select a folder first")
                return

            # Confirmation dialog with more detailed message
            reply = QMessageBox.question(
                self,
                'Confirm Cleanup',
                'This will:\n'
                '- Delete all aniinfo.json files in the subdirectories\n'
                '- Remove corresponding database entries\n'
                '\nThis action cannot be undone. Continue?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

            self.setUIEnabled(False)
            self.ui.progressBar.setVisible(True)

            # Count total subdirectories
            total_folders = sum(1 for entry in os.scandir(folder_path) if entry.is_dir())
            self.ui.progressBar.setMaximum(total_folders)
            current_progress = 0

            files_removed = 0
            errors = []
            remaining_valid_paths = []

            # First phase: Remove JSON files
            self.logger.info("Starting JSON files cleanup")
            for anime_folder in os.scandir(folder_path):
                if anime_folder.is_dir():
                    json_path = Path(anime_folder.path) / "aniinfo.json"
                    try:
                        if json_path.exists():
                            json_path.unlink()
                            files_removed += 1
                            self.logger.info(f"Removed: {json_path}")
                        else:
                            # Keep track of valid anime folders even if they don't have JSON
                            remaining_valid_paths.append(anime_folder.path)
                    except Exception as e:
                        error_msg = f"Error removing {json_path}: {str(e)}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)

                    current_progress += 1
                    self.ui.progressBar.setValue(current_progress)
                    QApplication.processEvents()

            # Second phase: Clean database
            self.logger.info("Starting database cleanup")
            try:
                db = AnimeDatabase(logger=self.logger)
                deleted_entries, removed_anime = db.clean_database(remaining_valid_paths)

                # Clear the anime list widget
                self.ui.listHentai.clear()

                # Final status update
                status = (f"Removed {files_removed} JSON files and {deleted_entries} database entries"
                                 f"{f' with {len(errors)} errors' if errors else ''}")

                if removed_anime:
                    self.logger.info("Removed anime from database: " +
                                    ", ".join(removed_anime[:5]) +
                                    f"{'... and more' if len(removed_anime) > 5 else ''}")

                self.ui.lOutput.setText(status)
                self.logger.info(f"Cleanup completed: {status}")

            except Exception as e:
                self.logger.error(f"Database cleanup error: {str(e)}")
                self.ui.lOutput.setText(f"Error during database cleanup: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error during clean operation: {str(e)}")
            self.ui.lOutput.setText(f"Error during cleaning: {str(e)}")
        finally:
            self.setUIEnabled(True)
            QTimer.singleShot(2000, lambda: self.ui.progressBar.setVisible(False))

    def cancel_processing(self):
        """Handler für Cancel-Button"""
        if hasattr(self, 'worker'):
            self.logger.info("Cancel requested by user")
            self.ui.bCancel.setEnabled(False)
            self.ui.bCancel.setText("Canceling...")
            self.ui.lOutput.setText("Canceling operation...")
            self.worker.cancel()

    def setUIEnabled(self, enabled: bool):
        """Enable or disable UI elements during processing."""
        self.ui.bSearchFolder.setEnabled(enabled)
        self.ui.bUpdateTags.setEnabled(enabled)
        self.ui.bGetHentai.setEnabled(enabled)
        self.ui.cleanButton.setEnabled(enabled)
        self.ui.bRename.setEnabled(enabled)
        if enabled:
            self.ui.progressBar.setValue(0)
            self.ui.progressBar.setVisible(False)

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = Widget()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error: {str(e)}")  # Fallback wenn Logger noch nicht initialisiert
