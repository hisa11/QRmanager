# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_device.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(449, 266)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.textEdit_2 = QTextEdit(Form)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setMinimumSize(QSize(431, 41))
        self.textEdit_2.setMaximumSize(QSize(431, 41))

        self.verticalLayout.addWidget(self.textEdit_2)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.textEdit = QTextEdit(Form)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setMinimumSize(QSize(431, 41))
        self.textEdit.setMaximumSize(QSize(431, 41))

        self.verticalLayout.addWidget(self.textEdit)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.textEdit_3 = QTextEdit(Form)
        self.textEdit_3.setObjectName(u"textEdit_3")
        self.textEdit_3.setMinimumSize(QSize(431, 41))
        self.textEdit_3.setMaximumSize(QSize(431, 41))

        self.verticalLayout.addWidget(self.textEdit_3)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(381, 41))
        self.pushButton.setMaximumSize(QSize(381, 41))
        font = QFont()
        font.setPointSize(17)
        self.pushButton.setFont(font)

        self.verticalLayout.addWidget(self.pushButton)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u30c7\u30d0\u30a4\u30b9\u306e\u7a2e\u985e\u3092\u5165\u529b", None))
        self.label.setText(QCoreApplication.translate("Form", u"ID\u5165\u529b", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u96fb\u5727\u3092\u8ffd\u52a0", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"ID\u3092\u8ffd\u52a0", None))
    # retranslateUi

