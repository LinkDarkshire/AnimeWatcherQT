import os

class HentaiFolderReader:
    def __init__(self, root_folder):
        self.root_folder = root_folder

    def get_hentai_names(self):
        """Liefert eine Liste von Hentai-Namen basierend auf den Unterordnern."""
        try:
            return [folder for folder in os.listdir(self.root_folder) if os.path.isdir(os.path.join(self.root_folder, folder))]
        except Exception as e:
            print(f"Error reading the folder: {e}")
            return []
