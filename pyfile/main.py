import sound_player
import look
import time
from datetime import datetime
import json
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer
from new_device_manager import DeviceManager
from UI.window import Ui_MainWindow
import PySide6.QtWidgets as Qw
import cv2
import sys
import os
import shutil  # 追加（不要なら削除可）

# pyfile ディレクトリをモジュール検索パスに追加
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'pyfile')))


camera_id = 0
delay = 30  # ミリ秒単位でタイマーの遅延を設定

qcd = cv2.QRCodeDetector()
global_data = {}

class SubWindow(QWidget):
  """ 別ウィンドウ（サブウィンドウ）"""

  def __init__(self):
    super().__init__()
    self.setWindowTitle("サブウィンドウ")
    self.setGeometry(200, 200, 300, 200)  # 位置(x, y)とサイズ(幅, 高さ)

class QRManager(Qw.QMainWindow):
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # Linux用: CAP_DSHOWを削除
    self.cap = cv2.VideoCapture(camera_id)

    self.timer = QTimer()
    self.timer.timeout.connect(self.update_frame)
    self.timer.start(delay)

    # シグナル接続はここで一度だけ行う
    self.ui.debise.clicked.connect(self.on_debise_clicked)
    self.ui.new_debise.clicked.connect(self.on_new_debise_clicked)

    self.QRframe_layout = Qw.QVBoxLayout(self.ui.QRframe)
    self.video_label = Qw.QLabel()
    self.QRframe_layout.addWidget(self.video_label)

    # data.jsonの絶対パス化
    data_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../data.json"))
    with open(data_path, "r", encoding="utf-8") as f:
      self.data = json.load(f)
      global_data = self.data

    self.last_detection_time = 0.0

    self.write_lending()

    self.list_window = None

    # 定期的に data.json を読み直すタイマーを設定（1秒周期）
    self.data_timer = QTimer()
    self.data_timer.timeout.connect(self.reload_data)
    self.data_timer.start(1000)  # 1秒ごとに読み直し

    # 新たに3秒後にテキストをクリアするタイマーを設定
    self.clear_timer = QTimer()
    self.clear_timer.setSingleShot(True)
    self.clear_timer.timeout.connect(self.ui.textBrowser.clear)

    # 写真フォルダの古い画像を削除
    self.cleanup_old_pictures()

  def update_frame(self):
    ret, frame = self.cap.read()
    if ret:
      # カメラ映像を左右反転
      frame = cv2.flip(frame, 1)
      ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
      if ret_qr:
        now_time = time.time()
        if now_time - self.last_detection_time >= 2.0:
          for s, p in zip(decoded_info, points):
            if s:
              self.handle_qr_code(s)
              color = (0, 255, 0)
            else:
              color = (0, 0, 255)
            frame = cv2.polylines(
                frame, [p.astype(int)], True, color, 8)
          self.last_detection_time = now_time

      # フレームをRGBに変換
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      height, width, channel = frame.shape
      bytes_per_line = 3 * width
      q_img = QImage(frame.data, width, height,
                     bytes_per_line, QImage.Format.Format_RGB888)
      pixmap = QPixmap.fromImage(q_img)

      # QLabelに表示
      self.video_label.setPixmap(pixmap)

  def handle_qr_code(self, qr_id):
    self.clear_timer.stop()  # 既存のクリアタイマーをリセット
    found_device = None
    for dev in self.data["devices"]:
      if dev["ID"] == qr_id:
        found_device = dev
        break

    self.ui.textBrowser.clear()   # 文字を即時クリア
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # pictureディレクトリの絶対パス化
    picture_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../picture"))
    os.makedirs(picture_dir, exist_ok=True)
    picture_filename = f"{qr_id}_{now.replace(':', '-')}.png"
    picture_path = os.path.join(picture_dir, picture_filename)
    relative_picture_path = f"picture/{picture_filename}"

    # 写真撮影・保存
    ret_cap, capture_frame = self.cap.read()
    if ret_cap:
      cv2.imwrite(picture_path, capture_frame)

    def display_message():
      if not found_device:
        sound_player.play_sound(os.path.abspath(os.path.join(
            os.path.dirname(__file__), "../sound/Alarm.mp3")))
        self.ui.textBrowser.append("このデバイスは登録されていません")
      else:
        self.ui.textBrowser.append(found_device["ID"])
        if not found_device.get("borrowed", False):
          self.ui.textBrowser.append("<span style='font-size:32pt;'>貸出</span>")
          found_device["borrowed"] = True
          found_device["last_image"] = relative_picture_path  # 相対パスで保存
          self.write_log(["貸出", now, found_device["ID"], relative_picture_path])
          self.write_lending()
          sound_player.play_sound(os.path.abspath(os.path.join(
              os.path.dirname(__file__), "../sound/Beep01.mp3")))
        else:
          self.ui.textBrowser.append("<span style='font-size:32pt;'>返却</span>")
          voltage = found_device.get("voltage", "不明")
          self.ui.textBrowser.append(
              f"<span style='font-size:32pt;'>電圧は{voltage}ですか？</span>")
          found_device["borrowed"] = False
          found_device["last_image"] = relative_picture_path  # 相対パスで保存
          self.write_log(["返却", now, found_device["ID"], relative_picture_path])
          self.write_lending()
          sound_player.play_sound(os.path.abspath(os.path.join(
              os.path.dirname(__file__), "../sound/Beep02.mp3")))
        # data.jsonの絶対パス化
        data_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "../data.json"))
        with open(data_path, "w", encoding="utf-8") as f:
          json.dump(self.data, f, ensure_ascii=False, indent=4)
      # 最新の読み取りから3秒後にテキストをクリア（新たな読み取りがあればリセットされる）
      self.clear_timer.start(3000)

    QTimer.singleShot(100, display_message)

  def write_log(self, row_data):
    log_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../log.csv"))
    with open(log_path, "a", encoding="utf-8") as f:
      f.write(",".join(row_data) + "\n")

  def closeEvent(self, event):
    self.cap.release()
    cv2.destroyAllWindows()
    event.accept()

  def on_new_debise_clicked(self):
    print("new_debiseボタンが押されました。")
    self.device_manager = DeviceManager()
    self.device_manager.add_device()
  # def on_new_user_clicked(self):
  #     print("new_userボタンが押されました。")

  def on_debise_clicked(self):
    print("debiseボタンが押されました。")
    look.open_list()

  def write_lending(self):
    self.ui.lending.clear()  # ← 一度クリアして再描画
    borrowed_devices = [dev["ID"]
                        for dev in self.data["devices"] if dev.get("borrowed", False)]
    self.ui.lending.append("貸出中のデバイス一覧:")
    for dev_id in borrowed_devices:
      self.ui.lending.append(dev_id)

  def reload_data(self):
    data_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../data.json"))
    with open(data_path, "r", encoding="utf-8") as f:
      self.data = json.load(f)
    self.write_lending()  # データを再読み込みした後に表示を更新

  def cleanup_old_pictures(self):
    """pictureフォルダ内の1週間以上前の画像ファイルを削除"""
    picture_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../picture"))
    if not os.path.exists(picture_dir):
      return
    now = time.time()
    one_week = 7 * 24 * 60 * 60
    for filename in os.listdir(picture_dir):
      file_path = os.path.join(picture_dir, filename)
      if os.path.isfile(file_path):
        try:
          mtime = os.path.getmtime(file_path)
          if now - mtime > one_week:
            os.remove(file_path)
        except Exception as e:
          print(f"ファイル削除エラー: {file_path} ({e})")

if __name__ == '__main__':
  app = Qw.QApplication(sys.argv)
  main_window = QRManager()
  main_window.showMaximized()  # 最初から最大化表示
  sys.exit(app.exec())
