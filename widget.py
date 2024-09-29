# This Python file uses the following encoding: utf-8
import sys
import os
import time
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from AniDBClient import AniDBClient  # Stellen Sie sicher, dass diese Funktion korrekt importiert wird
from HentaiDatabase import HentaiDatabase
from HentaiJSON import AnimeInfoManager
from TagListUpdater import TagListUpdater
from TagIDReader import TagIDReader


# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.initUI()

    def initUI(self):
        self.ui.bSearchFolder.clicked.connect(self.selectFolder)
        self.ui.bUpdateTags.clicked.connect(self.update_tags)

    def selectFolder(self):
        # Display dialog to select folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.pathLineEdit.setText(folder_path)
            self.processFolder(folder_path)
            def processFolder(self, folder_path):
                db = HentaiDatabase()
                aniDB_client = AniDBClient("AniDBLogin")
                tagreader = TagIDReader();

                # Use folder names as anime names and fetch information
                for anime_name in os.listdir(folder_path):
                    full_path = os.path.join(folder_path, anime_name)
                    if os.path.isdir(full_path):
                        # Check if anime already exists in the database
                        if not db.anime_exists(anime_name):
                            hson = AnimeInfoManager(full_path)
                            if not hson.check_file_existence():
                                anime_info = aniDB_client.query_anidb(anime_name)
                                anime_info['tag_name_list'] = tagreader.get_names_by_ids(anime_info['tag_id_list'])
                                #full_path = self.synchronize_folder_names(anime_info,full_path
                                hson.create_json(anime_info)
                                db.add_anime(anime_info,full_path)
                                self.displayAnimeInfo(anime_info)
                            else:
                                if hson.check_data_integrity:
                                    anime_info = hson.read_json()
                                    db.add_anime(anime_info,full_path)
                                    self.displayAnimeInfo(anime_info)
                                else:
                                    anime_info = aniDB_client.query_anidb(anime_name)
                                    #full_path = self.synchronize_folder_names(anime_info,full_path)
                                    db.add_anime(anime_info,full_path)
                                    self.displayAnimeInfo(anime_info)
                        else:
                            self.ui.lOutput.setText(f"{anime_name} already in the database, skipping API call.")
                aniDB_client.close()

    def displayAnimeInfo(self, anime_info):
    # Display anime information in the list widget
        item_text = f"{anime_info['romaji']} - {anime_info['ep_count']} Episodes"
        self.infoListWidget.addItem(item_text)

    def update_tags(self):
        # Create updater and thread
        self.thread = QThread()
        self.updater = TagListUpdater()  # Instantiate your TagListUpdater
    
        # Connect signals and slots
        self.updater.finished.connect(self.on_update_finished)  # Handle completion
    
        # Move updater to separate thread
        self.updater.moveToThread(self.thread)
    
        # Start the `update_tags_json` method of the updater in the new thread
        self.thread.started.connect(self.updater.update_tags_json)
    
        # Start the thread
        self.thread.start()
    
        # Disable the button while the thread is running
        self.ui.bUpdateTags.setEnabled(False)
    
    def on_update_finished(self):
        # When the updater is finished, cleanly terminate the thread
        self.thread.quit()  # Quit the thread
        self.thread.wait()  # Wait until the thread is completely finished
    
        # Delete updater and thread after completion
        self.updater.deleteLater()
        self.thread.deleteLater()
    
        # Reactivate the button after thread completion
        self.ui.bUpdateTags.setEnabled(True)

# Create QApplication and Widget instances
app = QApplication(sys.argv)
window = Widget()
window.show()
sys.exit(app.exec())
