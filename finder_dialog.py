from PyQt5.QtWidgets import QDialog, QLineEdit,QVBoxLayout, QLabel,QPushButton
import pyperclip

class AniDBFinderDialog(QDialog):
    """
    A dialog window for users to input the ID of a hentai from AniDB when the anime name cannot be found.

    Attributes:
    - anime_name: The name of the anime that could not be found.
    - idHentaiLine: A QLineEdit widget for users to input the ID.
    - okButton: A QPushButton widget for confirming the input.
    - cancelButton: A QPushButton widget for canceling the input.

    Methods:
    - __init__(self, animename): Initializes the dialog window with the given anime name.
    - initUI(self): Sets up the user interface of the dialog window.
    - accept(self): Retrieves the input ID and closes the dialog window.
    - GetID(self): Returns the input ID.
    """

    def __init__(self, animename):
        """
        Initializes the dialog window with the given anime name.

        Parameters:
        - animename (str): The name of the anime that could not be found.
        """
        super().__init__()
        self.anime_name = animename
        self.initUI()

    def initUI(self):
        """
        Sets up the user interface of the dialog window.
        """
        self.setWindowTitle("Couldn't find the Anime Name")
        layout = QVBoxLayout(self)

        # Primary provider combo box
        self.idHentaiLine = QLineEdit(self)
        #self.primaryComboBox.currentIndexChanged.connect(self.updateSecondaryComboBox)
        layout.addWidget(QLabel("Anime Name: {}".format(self.anime_name)))
        layout.addWidget(QLabel("Enter the ID of the Hentai from AniDB:"))
        layout.addWidget(self.idHentaiLine)

        # OK and Cancel buttons
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton = QPushButton("Save Anime Name")
        self.saveButton.clicked.connect(self.saveAnimeName)

        layout.addWidget(self.okButton)
        layout.addWidget(self.cancelButton)
        layout.addWidget(self.saveButton)

        self.setLayout(layout)

    def accept(self):
        """
        Retrieves the input ID and closes the dialog window.
        """
        self.id_text = self.idHentaiLine.text()
        super().accept()

    def GetID(self):
        """
        Returns the input ID.

        Returns:
        - str: The input ID.
        """
        return self.id_text
    def saveAnimeName(self):
        """
        Saves the anime name to memory.
        """
        pyperclip.copy(self.anime_name)
