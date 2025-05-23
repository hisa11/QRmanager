import cv2
import numpy as np
from pyzbar import pyzbar
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QSlider
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
import sys
from collections import deque
import time

class QRManager(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("拡張 QR リーダー")

    # カメラ設定（高解像度）
    self.cap = cv2.VideoCapture(0)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # QRコード検出用パラメータ
    self.adaptive_threshold = True
    self.use_edge_enhancement = True
    self.blur_size = 5
    self.last_detected_codes = deque(maxlen=5)  # 最近検出されたQRコード
    self.last_detection_time = 0

    # UIセットアップ
    central = QWidget()
    self.setCentralWidget(central)
    main_layout = QVBoxLayout(central)

    # ビデオ表示用ウィジェット
    self.video_label = QLabel()
    main_layout.addWidget(self.video_label)

    # 検出結果表示用ラベル
    self.result_label = QLabel("QRコードを検出中...")
    self.result_label.setStyleSheet(
        "font-size: 14pt; color: green; background-color: #f0f0f0; padding: 5px;")
    main_layout.addWidget(self.result_label)

    # コントロールパネル
    controls = QHBoxLayout()

    # 適応型しきい値処理の切り替えボタン
    self.threshold_btn = QPushButton("適応型しきい値: オン")
    self.threshold_btn.clicked.connect(self.toggle_threshold)
    controls.addWidget(self.threshold_btn)

    # エッジ強調の切り替えボタン
    self.edge_btn = QPushButton("エッジ強調: オン")
    self.edge_btn.clicked.connect(self.toggle_edge)
    controls.addWidget(self.edge_btn)

    # ブラーサイズ調整スライダー
    blur_layout = QVBoxLayout()
    blur_label = QLabel("ブラーサイズ:")
    self.blur_slider = QSlider(Qt.Horizontal)
    self.blur_slider.setMinimum(1)
    self.blur_slider.setMaximum(15)
    self.blur_slider.setValue(5)
    self.blur_slider.setTickInterval(2)
    self.blur_slider.setTickPosition(QSlider.TicksBelow)
    self.blur_slider.valueChanged.connect(self.update_blur_size)
    blur_layout.addWidget(blur_label)
    blur_layout.addWidget(self.blur_slider)
    controls.addLayout(blur_layout)

    main_layout.addLayout(controls)

    # タイマーでフレーム更新
    self.timer = QTimer(self)
    self.timer.timeout.connect(self.update_frame)
    self.timer.start(30)

  def toggle_threshold(self):
    self.adaptive_threshold = not self.adaptive_threshold
    self.threshold_btn.setText(
        f"適応型しきい値: {'オン' if self.adaptive_threshold else 'オフ'}")

  def toggle_edge(self):
    self.use_edge_enhancement = not self.use_edge_enhancement
    self.edge_btn.setText(
        f"エッジ強調: {'オン' if self.use_edge_enhancement else 'オフ'}")

  def update_blur_size(self, value):
    # 奇数値に調整
    self.blur_size = value if value % 2 == 1 else value + 1

  def enhance_image(self, frame):
    # グレースケール変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 基本的な前処理
    equalized = cv2.equalizeHist(gray)

    # ガウシアンブラー
    blurred = cv2.GaussianBlur(equalized, (self.blur_size, self.blur_size), 0)

    # 適応型しきい値処理
    if self.adaptive_threshold:
      thresh = cv2.adaptiveThreshold(
          blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
          cv2.THRESH_BINARY, 11, 2)
    else:
      _, thresh = cv2.threshold(
          blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # エッジ強調
    if self.use_edge_enhancement:
      edges = cv2.Canny(blurred, 100, 200)
      kernel = np.ones((3, 3), np.uint8)
      edges = cv2.dilate(edges, kernel, iterations=1)
      # エッジを元の画像に追加
      enhanced = cv2.addWeighted(thresh, 0.7, edges, 0.3, 0)
    else:
      enhanced = thresh

    # ノイズ除去のためのモーフォロジー演算
    kernel = np.ones((3, 3), np.uint8)
    enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, kernel)
    enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)

    return enhanced, gray, thresh

  def update_frame(self):
    ret, frame = self.cap.read()
    if not ret:
      return

    # 前処理
    frame = cv2.flip(frame, 1)

    # 複数の画像処理パイプライン
    enhanced, gray, thresh = self.enhance_image(frame)

    # 処理された画像でQRコード検出を試みる
    barcodes = pyzbar.decode(enhanced)

    # 標準のグレースケールでもバックアップとして試行
    if not barcodes:
      barcodes = pyzbar.decode(gray)

    # 元の画像でも試行（前処理がうまくいかない場合のフォールバック）
    if not barcodes:
      barcodes = pyzbar.decode(frame)

    display_frame = frame.copy()  # 表示用の画像コピー

    for barcode in barcodes:
      x, y, w, h = barcode.rect

      # バウンディングボックス描画（より目立つように設定）
      cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

      # QRコードの隅にマーカーを追加
      cv2.circle(display_frame, (x, y), 10, (0, 0, 255), -1)  # 左上
      cv2.circle(display_frame, (x + w, y), 10, (0, 0, 255), -1)  # 右上
      cv2.circle(display_frame, (x, y + h), 10, (0, 0, 255), -1)  # 左下
      cv2.circle(display_frame, (x + w, y + h), 10, (0, 0, 255), -1)  # 右下

      # データとタイプ取得
      data = barcode.data.decode('utf-8')
      barcode_type = barcode.type

      # テキスト表示（より見やすく）
      text = f"{data} ({barcode_type})"
      cv2.putText(display_frame, text, (x, y - 15),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

      # 検出されたQRコードを履歴に追加
      curr_time = time.time()
      self.last_detected_codes.append((data, curr_time))
      self.last_detection_time = curr_time

      # 検出結果をラベルに表示
      self.result_label.setText(f"検出: {data} ({barcode_type})")

    # 前回検出から2秒以上経過している場合、検出中メッセージに戻す
    if time.time() - self.last_detection_time > 2 and self.last_detection_time > 0:
      self.result_label.setText("QRコードを検出中...")

    # 処理方法を画面に表示（デバッグ用）
    method_text = f"処理: {'適応型' if self.adaptive_threshold else 'Otsu'}, "
    method_text += f"エッジ強調: {'オン' if self.use_edge_enhancement else 'オフ'}, "
    method_text += f"ブラーサイズ: {self.blur_size}"
    cv2.putText(display_frame, method_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # デバッグ用に処理経過を表示
    debug_display = np.hstack([
        cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    ])
    debug_display = cv2.resize(debug_display, (display_frame.shape[1], 150))
    display_with_debug = np.vstack([display_frame, debug_display])

    # Qt表示用に変換
    rgb = cv2.cvtColor(display_with_debug, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
    self.video_label.setPixmap(QPixmap.fromImage(img))

  def closeEvent(self, event):
    self.cap.release()
    cv2.destroyAllWindows()
    super().closeEvent(event)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = QRManager()
  window.show()
  sys.exit(app.exec())
