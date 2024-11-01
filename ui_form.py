# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QListWidget, QListWidgetItem,
    QProgressBar, QPushButton, QSizePolicy, QTextEdit,
    QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(800, 600)
        self.bSearchFolder = QPushButton(Widget)
        self.bSearchFolder.setObjectName(u"bSearchFolder")
        self.bSearchFolder.setGeometry(QRect(680, 40, 101, 31))
        self.bSearchFolder.setAutoDefault(False)
        self.bSearchFolder.setFlat(False)
        self.textEdit_2 = QTextEdit(Widget)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(20, 90, 621, 31))
        self.tPath = QTextEdit(Widget)
        self.tPath.setObjectName(u"tPath")
        self.tPath.setGeometry(QRect(20, 40, 621, 31))
        self.tPath.setReadOnly(True)
        self.bUpdateTags = QPushButton(Widget)
        self.bUpdateTags.setObjectName(u"bUpdateTags")
        self.bUpdateTags.setGeometry(QRect(20, 500, 101, 31))
        self.label = QLabel(Widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 30, 37, 12))
        self.label_2 = QLabel(Widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 80, 37, 12))
        self.bRename = QPushButton(Widget)
        self.bRename.setObjectName(u"bRename")
        self.bRename.setGeometry(QRect(680, 140, 101, 31))
        self.bGetHentai = QPushButton(Widget)
        self.bGetHentai.setObjectName(u"bGetHentai")
        self.bGetHentai.setGeometry(QRect(680, 90, 101, 31))
        self.lOutput = QLabel(Widget)
        self.lOutput.setObjectName(u"lOutput")
        self.lOutput.setGeometry(QRect(20, 540, 761, 16))
        self.listHentai = QListWidget(Widget)
        self.listHentai.setObjectName(u"listHentai")
        self.listHentai.setGeometry(QRect(20, 140, 621, 192))
        self.progressBar = QProgressBar(Widget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setEnabled(False)
        self.progressBar.setGeometry(QRect(20, 560, 761, 23))
        self.progressBar.setLocale(QLocale(QLocale.German, QLocale.Germany))
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)
        self.cleanButton = QPushButton(Widget)
        self.cleanButton.setObjectName(u"cleanButton")
        self.cleanButton.setGeometry(QRect(680, 190, 101, 31))
        self.cleanButton.setLocale(QLocale(QLocale.German, QLocale.Germany))

        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Lewd Watcher", None))
        self.bSearchFolder.setText(QCoreApplication.translate("Widget", u"Search Folder", None))
        self.bUpdateTags.setText(QCoreApplication.translate("Widget", u"Update Tags", None))
        self.label.setText(QCoreApplication.translate("Widget", u"Path:", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"Search:", None))
        self.bRename.setText(QCoreApplication.translate("Widget", u"Rename", None))
        self.bGetHentai.setText(QCoreApplication.translate("Widget", u"Get Animes", None))
        self.lOutput.setText("")
        self.cleanButton.setText(QCoreApplication.translate("Widget", u"Clean up", None))
    # retranslateUi

