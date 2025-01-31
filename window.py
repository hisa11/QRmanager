# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QListView,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTextBrowser, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(876, 573)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.debise = QPushButton(self.centralwidget)
        self.debise.setObjectName(u"debise")

        self.gridLayout.addWidget(self.debise, 0, 0, 1, 1)

        self.new_debise = QPushButton(self.centralwidget)
        self.new_debise.setObjectName(u"new_debise")

        self.gridLayout.addWidget(self.new_debise, 0, 1, 1, 1)

        self.new_user = QPushButton(self.centralwidget)
        self.new_user.setObjectName(u"new_user")

        self.gridLayout.addWidget(self.new_user, 0, 2, 1, 1)

        self.QRframe = QFrame(self.centralwidget)
        self.QRframe.setObjectName(u"QRframe")
        self.QRframe.setMinimumSize(QSize(471, 471))
        self.QRframe.setMaximumSize(QSize(471, 471))
        self.QRframe.setFrameShape(QFrame.Shape.StyledPanel)
        self.QRframe.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout.addWidget(self.QRframe, 1, 0, 2, 3)

        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setMinimumSize(QSize(381, 181))

        self.gridLayout.addWidget(self.textBrowser, 1, 3, 1, 1)

        self.lending = QListView(self.centralwidget)
        self.lending.setObjectName(u"lending")
        self.lending.setMinimumSize(QSize(381, 281))

        self.gridLayout.addWidget(self.lending, 2, 3, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 876, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.debise.setText(QCoreApplication.translate("MainWindow", u"\u767b\u9332\u6a5f\u5668\u4e00\u89a7", None))
        self.new_debise.setText(QCoreApplication.translate("MainWindow", u"\u6a5f\u5668\u767b\u9332", None))
        self.new_user.setText(QCoreApplication.translate("MainWindow", u"\u30e6\u30fc\u30b6\u30fc\u8ffd\u52a0", None))
    # retranslateUi

