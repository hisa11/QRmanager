import cv2
import PySide6.QtWidgets as Qw
from UI.new_device import Ui_Form
from PySide6.QtGui import QImage, QPixmap
import PySide6
import sys
import json
import PySide6
import sound_player

class DeviceManager(Qw.QWidget):
  def __init__(self):
    super().__init__()
    # self.initUI()

  # def initUI(self):
  #     self.setWindowTitle('Device Manager')
  #     self.setGeometry(100, 100, 800, 600)
  #     self.show()

  def add_device(self):
    # 新しいデバイスを登録するウィンドウを表示
    self.new_device_window = Qw.QWidget()
    self.new_device_ui = Ui_Form()
    self.new_device_ui.setupUi(self.new_device_window)
    # ウィンドウのリサイズを禁止
    self.new_device_window.setFixedSize(self.new_device_window.size())
    # テキストエディットの改行を禁止
    self.new_device_ui.textEdit_2.setAcceptRichText(False)
    self.new_device_ui.textEdit.setAcceptRichText(False)
    # # 数字と小数点のみ入力可能にするバリデータ
    # double_validator = QRegularExpressionValidator(
    #     QtCore.QRegularExpression(r"^[0-9.]+$"))
    # self.new_device_ui.textEdit_3.setValidator(double_validator)
    self.new_device_ui.textEdit_3.textChanged.connect(
        self.validate_voltage_input)

    self.new_device_ui.pushButton.clicked.connect(self.save_device)
    self.new_device_window.show()

  def validate_voltage_input(self):
    text = self.new_device_ui.textEdit_3.toPlainText()
    try:
      if text:
        float(text)
    except ValueError:
      # 無効な入力の場合、テキストをクリアする
      self.new_device_ui.textEdit_3.setText(text[:-1])

  def save_device(self):
    # 入力されたデバイス情報を取得
    device_type = self.new_device_ui.textEdit_2.toPlainText()
    device_id = self.new_device_ui.textEdit.toPlainText()
    device_voltage = self.new_device_ui.textEdit_3.toPlainText()

    # デバイス情報を辞書形式で作成
    new_device = {
        "devise": device_type,
        "ID": device_id,
        "voltage": device_voltage,
        "borrowed": False
    }

    # バリデーション
    if not device_type or not device_id or not device_voltage:
      Qw.QMessageBox.critical(self, "エラー", "すべてのフィールドを入力してください。")
      return
    try:
      float(device_voltage)
    except ValueError:
      Qw.QMessageBox.critical(self, "エラー", "電圧は数値を入力してください。")
      return

    # data.json にデバイス情報を追加
    try:
      with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    except FileNotFoundError:
      data = {"devices": []}

    # 同じIDを持つデバイスがすでに登録されていないか確認
    for device in data["devices"]:
      if device["ID"] == device_id:
        Qw.QMessageBox.warning(self, "警告", "同じIDを持つデバイスがすでに登録されています。")
        return

    data["devices"].append(new_device)
    with open("data.json", "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)

    # 入力フィールドをクリア
    self.new_device_ui.textEdit_2.clear()
    self.new_device_ui.textEdit.clear()
    self.new_device_ui.textEdit_3.clear()

    # 登録完了音を再生
    sound_player.play_sound("./sound/Beep02.mp3")

    # # ウィンドウを閉じる
    # self.new_device_window.close()

if __name__ == '__main__':
  app = Qw.QApplication(sys.argv)
  manager = DeviceManager()
  manager.add_device()
  sys.exit(app.exec())
