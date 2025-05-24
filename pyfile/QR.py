import cv2
import numpy as np
from pyzbar import pyzbar
import zbar  # ZBar APIを直接使用
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QSlider, QComboBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
import sys
from collections import deque
import time
import logging
import os
import json

# OpenCVの警告を完全に抑制
logging.basicConfig(level=logging.ERROR)
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"  # OpenCVの環境変数でログを制御
os.environ["OPENCV_VIDEOIO_DEBUG"] = "0"  # ビデオI/O警告を無効化

class QRManager(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("高度な QR リーダー")

    # OpenCVのログレベルを設定（警告を非表示に）
    cv2.setLogLevel(cv2.LOG_LEVEL_SILENT)  # 完全に無音に設定

    # ZBarスキャナーの初期化
    self.scanner = zbar.ImageScanner()
    self.scanner.parse_config('enable')  # すべてのシンボルタイプを有効化

    # 検出エンジンの選択
    self.detection_engine = "hybrid"  # "pyzbar", "zbar", "hybrid"

    # QRコード検証用
    self.detection_counter = {}  # QRコードの内容と検出回数のマップ
    self.min_detection_count = 3  # 信頼できる検出とみなすための最小回数

    # カメラ設定（高解像度）
    self.cap = cv2.VideoCapture(0)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

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

    # 検出エンジン選択
    engine_layout = QVBoxLayout()
    engine_label = QLabel("検出エンジン:")
    self.engine_combo = QComboBox()
    self.engine_combo.addItems(["PyZbar", "ZBar", "ハイブリッド"])
    self.engine_combo.setCurrentIndex(2)  # ハイブリッドをデフォルトに
    self.engine_combo.currentIndexChanged.connect(self.change_detection_engine)
    engine_layout.addWidget(engine_label)
    engine_layout.addWidget(self.engine_combo)
    controls.addLayout(engine_layout)

    main_layout.addLayout(controls)

    # タイマーでフレーム更新
    self.timer = QTimer(self)
    self.timer.timeout.connect(self.update_frame)
    self.timer.start(15)  # 15msごとにフレーム更新

    # data.jsonの初回読み込み
    data_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../data.json"))
    with open(data_path, "r", encoding="utf-8") as f:
      self.data = json.load(f)
    self.data_path = data_path  # パスをメンバ変数に
    self.handle_lock = False    # スキャン処理中フラグ

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

  def change_detection_engine(self, index):
    engines = ["pyzbar", "zbar", "hybrid"]
    self.detection_engine = engines[index]
    # 検出カウンターをリセット
    self.detection_counter = {}

  def decode_with_zbar(self, gray_image):
    # ZBar用にグレースケール画像を変換
    height, width = gray_image.shape
    raw_image = gray_image.tobytes()

    # ZBarイメージを作成
    zbar_image = zbar.Image(width, height, 'Y800', raw_image)

    # スキャン実行
    self.scanner.scan(zbar_image)

    # 結果を取得
    results = []
    for symbol in zbar_image:
      # バーコード情報を抽出
      data = symbol.data.decode('utf-8')
      type_name = symbol.type

      # 位置情報
      points = symbol.location
      x0, y0 = points[0]
      x2, y2 = points[2]
      x, y = min(x0, x2), min(y0, y2)
      w, h = abs(x2 - x0), abs(y2 - y0)

      # pyzbarの結果と似た形式で返す
      class BarCodeResult:
        pass

      result = BarCodeResult()
      result.data = data.encode('utf-8')  # バイト列に戻す
      result.type = str(type_name)
      result.rect = (x, y, w, h)

      results.append(result)

    return results

  def enhance_image(self, frame):
    # グレースケール変換のみ（前処理を最小限に）
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray, gray, gray  # すべて同じ画像を返す

  def update_frame(self):
    ret, frame = self.cap.read()
    if not ret:
      return

    frame = cv2.flip(frame, 1)
    enhanced, gray, thresh = self.enhance_image(frame)

    barcodes = []
    # pyzbarには必ずグレースケール画像(gray)を渡す
    if self.detection_engine == "pyzbar" or self.detection_engine == "hybrid":
      pyzbar_codes = pyzbar.decode(gray)
      if not pyzbar_codes and self.detection_engine == "pyzbar":
        pyzbar_codes = pyzbar.decode(gray)
        if not pyzbar_codes:
          pyzbar_codes = pyzbar.decode(gray)
      barcodes.extend(pyzbar_codes)

    if self.detection_engine == "zbar" or (self.detection_engine == "hybrid" and not barcodes):
      zbar_codes = self.decode_with_zbar(gray)
      barcodes.extend(zbar_codes)

    display_frame = frame.copy()

    # 検証・スキップを完全になくす
    for barcode in barcodes:
      data = barcode.data.decode('utf-8')
      barcode_type = barcode.type
      x, y, w, h = barcode.rect

      # バウンディングボックス描画
      cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
      cv2.circle(display_frame, (x, y), 10, (0, 0, 255), -1)
      cv2.circle(display_frame, (x + w, y), 10, (0, 0, 255), -1)
      cv2.circle(display_frame, (x, y + h), 10, (0, 0, 255), -1)
      cv2.circle(display_frame, (x + w, y + h), 10, (0, 0, 255), -1)
      text = f"{data} ({barcode_type})"
      cv2.putText(display_frame, text, (x, y - 15),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

      self.result_label.setText(f"検出: {data} ({barcode_type})")
      self.handle_qr_code(data)  # 毎フレーム処理（必要ならここで連続処理防止も可）
      break  # 1フレームで1つだけ処理

    # 処理方法を画面に表示（デバッグ用）
    method_text = f"検出エンジン: {self.detection_engine}, "
    method_text += f"処理: {'適応型' if self.adaptive_threshold else 'Otsu'}, "
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

  def handle_qr_code(self, qr_id):
    # self.dataはインスタンス変数として保持し、ファイルから再読込しない
    found_device = None
    for dev in self.data["devices"]:
      if dev["ID"] == qr_id:
        found_device = dev
        break

    now = time.strftime("%Y-%m-%d %H:%M:%S")
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

    if found_device:
      if not found_device.get("borrowed", False):
        found_device["borrowed"] = True
        found_device["last_image"] = relative_picture_path
      else:
        found_device["borrowed"] = False
        found_device["last_image"] = relative_picture_path

      # data.jsonを即時保存（flushとfsyncで確実に書き込む）
      with open(self.data_path, "w", encoding="utf-8") as f:
        json.dump(self.data, f, ensure_ascii=False, indent=4)
        f.flush()
        os.fsync(f.fileno())

      # 書き込み直後に即時再読込してUIを更新
      self.reload_data()

  def reload_data(self):
    with open(self.data_path, "r", encoding="utf-8") as f:
      self.data = json.load(f)
    # UIの表示もここで更新
    self.write_lending()
