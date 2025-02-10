import cv2
import PySide6.QtWidgets as Qw
from window import Ui_MainWindow
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
import PySide6
import sys
import json
import os
from datetime import datetime
import time
from main import global_data  # グローバル変数をインポート
import PySide6
from PySide6 import QtCore
from PySide6 import QtWidgets
import os
import sys

dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

# グローバル変数でウィンドウの参照を保持
window_list = []

def open_list():
  global window_list
  app = Qw.QApplication.instance()
  if app is None:
    app = Qw.QApplication(sys.argv)

  window = Qw.QMainWindow()
  text_edit = Qw.QTextEdit()
  window.setCentralWidget(text_edit)
  window.setWindowTitle("New Window")
  window.resize(400, 300)

  with open("data.json", "r", encoding="utf-8") as f:
    device_data = json.load(f)

  text_edit.append("デバイス一覧:")
  for dev in device_data["devices"]:
    text_edit.append(dev["ID"])

  window.show()

  # ウィンドウへの参照を保持して即閉じられないようにする
  window_list.append(window)

  # 既にメインのイベントループが動作しているため app.exec() は不要

def write_list(self):
  # この関数は使用しないため削除または未使用のまま
  pass
