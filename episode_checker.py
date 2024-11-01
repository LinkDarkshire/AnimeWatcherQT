import os

class EpisodeChecker:
    def __init__(self, root_folder, hentai_data):
        """
        :param root_folder: Pfad zum Hauptordner mit den Hentai-Unterordnern.
        :param hentai_data: Ein Wörterbuch mit Hentai-Namen als Schlüssel und der erwarteten Episodenanzahl als Wert.
        """
        self.root_folder = root_folder
        self.hentai_data = hentai_data

    def check_missing_episodes(self):
        missing_episodes = {}

        for hentai, expected_count in self.hentai_data.items():
            hentai_folder = os.path.join(self.root_folder, hentai)
            if os.path.exists(hentai_folder):
                actual_count = len([f for f in os.listdir(hentai_folder) if os.path.isfile(os.path.join(hentai_folder, f))])
                if actual_count < expected_count:
                    missing_episodes[hentai] = expected_count - actual_count

        return missing_episodes

# Beispielverwendung:

root_folder = "/path/to/main/folder"
hentai_data = {
    "Naruto": 220,
    "Bleach": 366,
    # ... andere hentai-Namen und ihre erwarteten Episodenzahlen
}

checker = EpisodeChecker(root_folder, hentai_data)
missing = checker.check_missing_episodes()

for hentai, count in missing.items():
    print(f"{hentai} fehlen {count} Episoden.")
