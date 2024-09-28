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
from PySide6.QtWidgets import (QApplication, QLabel, QListView, QPushButton,
    QSizePolicy, QTextEdit, QWidget)

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
        self.textEdit = QTextEdit(Widget)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(20, 40, 621, 31))
        self.textEdit.setReadOnly(True)
        self.bUpdateTags = QPushButton(Widget)
        self.bUpdateTags.setObjectName(u"bUpdateTags")
        self.bUpdateTags.setGeometry(QRect(20, 527, 101, 31))
        self.label = QLabel(Widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 30, 37, 12))
        self.label_2 = QLabel(Widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 80, 37, 12))
        self.listView = QListView(Widget)
        self.listView.setObjectName(u"listView")
        self.listView.setGeometry(QRect(20, 140, 621, 192))
        self.bRename = QPushButton(Widget)
        self.bRename.setObjectName(u"bRename")
        self.bRename.setGeometry(QRect(679, 87, 101, 31))
        self.lOutput = QLabel(Widget)
        self.lOutput.setObjectName(u"lOutput")
        self.lOutput.setGeometry(QRect(20, 570, 751, 16))

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
        self.lOutput.setText("")
    # retranslateUi

