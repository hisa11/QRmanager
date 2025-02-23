import cv2
import PySide6.QtWidgets as Qw
from pyfile.UI.window import Ui_MainWindow
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
import sys
import json
import os
from datetime import datetime
import time

camera_id = 0
delay = 30  # ミリ秒単位でタイマーの遅延を設定

qcd = cv2.QRCodeDetector()

class QRManager(Qw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.cap = cv2.VideoCapture(camera_id)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        # self.timer.timeout.connect(self.write_lending)  # ← この行を削除
        self.timer.start(delay)

        self.QRframe_layout = Qw.QVBoxLayout(self.ui.QRframe)
        self.video_label = Qw.QLabel()
        self.QRframe_layout.addWidget(self.video_label)

        with open("data.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.last_detection_time = 0.0

        self.write_lending()


    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
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
        self.ui.debise.clicked.connect(self.on_debise_clicked)
        self.ui.new_debise.clicked.connect(self.on_new_debise_clicked)
        # self.ui.new_user.clicked.connect(self.on_new_user_clicked)

    def handle_qr_code(self, qr_id):
        found_device = None
        for dev in self.data["devices"]:
            if dev["ID"] == qr_id:
                found_device = dev
                break

        self.ui.textBrowser.clear()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        picture_path = os.path.join("picture", f"{qr_id}_{now.replace(':','-')}.png")

        # 写真撮影・保存
        ret_cap, capture_frame = self.cap.read()
        if ret_cap:
            cv2.imwrite(picture_path, capture_frame)

        if not found_device:
            self.ui.textBrowser.append("このデバイスは登録されていません")
            return

        self.ui.textBrowser.append(found_device["ID"])
        if not found_device.get("borrowed", False):
            # 貸出処理
            self.ui.textBrowser.append("<span style='font-size:32pt;'>貸出</span>")
            found_device["borrowed"] = True
            self.write_log(["貸出", now, found_device["ID"], picture_path])
            self.write_lending()  # ← 貸出時に更新
        else:
            # 返却処理
            self.ui.textBrowser.append("<span style='font-size:32pt;'>返却</span>")
            voltage = found_device.get("voltage", "不明")
            self.ui.textBrowser.append(f"<span style='font-size:32pt;'>電圧は{voltage}ですか？</span>")
            found_device["borrowed"] = False
            self.write_log(["返却", now, found_device["ID"], picture_path])
            self.write_lending()  # ← 返却時に更新

        # data.json を更新
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def write_log(self, row_data):
        with open("log.csv", "a", encoding="utf-8") as f:
            f.write(",".join(row_data) + "\n")

    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

    def on_debise_clicked(self):
        print("debiseボタンが押されました。")
    def on_new_debise_clicked(self):
        print("new_debiseボタンが押されました。")
    # def on_new_user_clicked(self):
    #     print("new_userボタンが押されました。")

    def write_lending(self):
        self.ui.lending.clear()  # ← 一度クリアして再描画
        borrowed_devices = [dev["ID"] for dev in self.data["devices"] if dev.get("borrowed", False)]
        self.ui.lending.append("貸出中のデバイス一覧:")
        for dev_id in borrowed_devices:
            self.ui.lending.append(dev_id)

if __name__ == '__main__':
    app = Qw.QApplication(sys.argv)
    main_window = QRManager()
    main_window.show()
    sys.exit(app.exec())
