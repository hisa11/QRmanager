from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import cv2
import json
import os
from datetime import datetime
import logging
import ssl
import base64
import threading  # スレッドロック用
import time

# グローバル変数で直近のQR処理を記録
last_qr_id = None
last_qr_time = 0

app = Flask(__name__, template_folder='../pages',
            static_folder='../static')  # テンプレートフォルダを変更
app.logger.setLevel(logging.INFO)

# SSL証明書と秘密鍵の読み込み
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('pages/key/server.crt', 'pages/key/server.key')

socketio = SocketIO(app, cors_allowed_origins="*")

camera_id = 0
qcd = cv2.QRCodeDetector()

# デバイスデータの読み込み
DATA_FILE = os.path.abspath("data.json")  # 絶対パスで指定
data_lock = threading.Lock()  # スレッドロックを作成

def load_data():
  with open(DATA_FILE, "r", encoding="utf-8") as f:
    return json.load(f)

def save_data(data):
  with data_lock:  # ロックを取得
    with open(DATA_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

@app.route('/')
def index():
  return render_template('index.html', devices=data["devices"])

@app.route('/pc')
def pc():
  return render_template('pc.html', devices=data["devices"])

@app.route('/scan', methods=['POST'])
def scan_qr():
  global last_qr_id, last_qr_time
  cap = cv2.VideoCapture(camera_id)
  try:
    ret, frame = cap.read()
    if not ret:
      app.logger.error("カメラからフレームが取得できませんでした")
      return jsonify({"status": "エラー", "device": None})

    ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
    if ret_qr:
      for s in decoded_info:
        if s:
          qr_id = s
          now_time = time.time()
          # 直近2秒以内に同じIDなら無視
          if qr_id == last_qr_id and (now_time - last_qr_time) < 2:
            return jsonify({"status": "スキップ", "device": None})
          last_qr_id = qr_id
          last_qr_time = now_time
          for i, dev in enumerate(data["devices"]):  # enumerateを使用
            if dev["ID"] == qr_id:
              found_device = dev
              break
          else:
            found_device = None
          if found_device:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 保存先フォルダがなければ作成
            os.makedirs("picture", exist_ok=True)
            picture_filename = f"{qr_id}_{now.replace(':', '-')}.png"
            picture_path = os.path.join("picture", picture_filename)
            # パスをWeb用に変換
            picture_path = picture_path.replace("\\", "/")
            cv2.imwrite(picture_path, frame)

            # 現在の状態を明示的に取得してから切り替え
            current_borrowed = found_device.get("borrowed", False)
            if current_borrowed:
              found_device["borrowed"] = False
              status = "返却"
            else:
              found_device["borrowed"] = True
              status = "貸出"

            # JSONファイルの更新
            app.logger.info(f"Updating device status: {found_device}")
            save_data(data)

            # log.csvに書き込む
            try:
              app.logger.info(
                  f"Writing to log.csv: {status},{now},{found_device['ID']},{picture_path}")
              with open("log.csv", "a", encoding="utf-8", newline='') as log_file:
                log_file.write(
                    f"{status},{now},{found_device['ID']},{picture_path}\n")
            except Exception as e:
              app.logger.error(
                  f"Failed to write to log.csv: {e}, type: {type(e)}, args: {e.args}")

            socketio.emit(
                'update', {'status': status, 'device': found_device})
            return jsonify({"status": status, "device": found_device})
          else:
            return jsonify({"status": "未登録", "device": None})
    return jsonify({"status": "エラー", "device": None})
  finally:
    cap.release()

@app.route('/upload_inner_photo', methods=['POST'])
def upload_inner_photo():
  req_data = request.get_json()
  qr_id = req_data.get('id')
  image_data = req_data.get('image')

  if not qr_id or not image_data:
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

  # 画像データをデコード
  image_data = image_data.split(',')[1]
  image_data = base64.b64decode(image_data)

  # 画像を保存
  now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  image_filename = f"{qr_id}_inner_{now.replace(':', '-')}.png"
  image_path = os.path.join("picture", image_filename)
  # パスをWeb用に変換
  image_path = image_path.replace("\\", "/")
  with open(image_path, 'wb') as f:
    f.write(image_data)

  # デバイス情報を取得（状態変更はしない）
  found_device = None
  for dev in data["devices"]:
    if dev["ID"] == qr_id:
      found_device = dev
      break

  if found_device:
    # last_imageのみ更新（状態は変更しない）
    found_device['last_image'] = image_path
    save_data(data)

    # log.csvに画像保存のみ記録
    try:
      app.logger.info(
          f"Writing image log to log.csv: 画像保存,{now},{qr_id},{image_path}")
      with open("log.csv", "a", encoding="utf-8", newline='') as log_file:
        log_file.write(f"画像保存,{now},{qr_id},{image_path}\n")
        log_file.flush()
    except Exception as e:
      app.logger.error(
          f"Failed to write to log.csv: {e}, type: {type(e)}, args: {e.args}")
      return jsonify({'status': 'error', 'message': 'Failed to write to log.csv'}), 500

    return jsonify({'status': 'success', 'path': image_path, 'device': found_device})
  else:
    # 未登録デバイスの場合も画像は保存
    try:
      app.logger.info(
          f"Writing image log to log.csv: 画像保存(未登録),{now},{qr_id},{image_path}")
      with open("log.csv", "a", encoding="utf-8", newline='') as log_file:
        log_file.write(f"画像保存(未登録),{now},{qr_id},{image_path}\n")
        log_file.flush()
    except Exception as e:
      app.logger.error(f"Failed to write to log.csv: {e}")
      return jsonify({'status': 'error', 'message': 'Failed to write to log.csv'}), 500

    return jsonify({'status': 'success', 'path': image_path, 'device': None})

  return jsonify({'status': 'success', 'path': image_path, 'device': found_device})

@app.route('/update_device_status', methods=['POST'])
def update_device_status():
  global last_qr_id, last_qr_time
  device_id = request.json.get('id')
  app.logger.info(f"Received device ID: {device_id}")

  # 直近2秒以内に同じIDなら無視
  now_time = time.time()
  if device_id == last_qr_id and (now_time - last_qr_time) < 2:
    return jsonify({"status": "skip", "message": "Skip duplicate scan"})

  last_qr_id = device_id
  last_qr_time = now_time

  # デバイスを検索
  for i, dev in enumerate(data["devices"]):
    if dev["ID"] == device_id:
      found_device = dev
      break
  else:
    found_device = None

  if found_device:
    # 写真撮影・保存
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs("picture", exist_ok=True)
    picture_filename = f"{device_id}_{now.replace(':', '-')}.png"
    picture_path = os.path.join("picture", picture_filename)
    picture_path = picture_path.replace("\\", "/")

    current_borrowed = found_device.get("borrowed", False)
    if current_borrowed:
      found_device["borrowed"] = False
      status = "返却"
    else:
      found_device["borrowed"] = True
      status = "貸出"

    found_device["last_image"] = picture_path

    # JSONファイルの更新
    app.logger.info(f"Updating device status: {found_device}")
    save_data(data)

    # log.csvに書き込む
    try:
      app.logger.info(
          f"Writing to log.csv: {status},{now},{found_device['ID']},{picture_path}")
      with open("log.csv", "a", encoding="utf-8", newline='') as log_file:
        log_file.write(f"{status},{now},{found_device['ID']},{picture_path}\n")
    except Exception as e:
      app.logger.error(f"Failed to write to log.csv: {e}")

    # 全クライアントに更新を通知
    socketio.emit('update', {'status': status, 'device': found_device})
    socketio.emit('update_all', {'devices': data["devices"]})

    app.logger.info(f"Device status updated: {device_id} - {status}")
    return jsonify({"status": "success", "device": found_device})
  else:
    app.logger.warning(f"Device not found: {device_id}")
    return jsonify({"status": "not_found", "message": "Device not found"})

@app.route('/devices', methods=['GET'])
def get_devices():
  return jsonify(data["devices"])

@app.route('/pages/picture_list.html')
def picture_list():
  with open("data.json", encoding="utf-8") as f:
    data = json.load(f)
  devices = data.get("devices", [])
  return render_template('picture_list.html', devices=devices)

@app.route('/sound/<filename>')
def sound(filename):
  return send_from_directory('../sound', filename)

@app.route('/picture/<path:filename>')
def picture(filename):
  return send_from_directory('../picture', filename)

@socketio.on('connect', namespace='/')
def test_connect():
  app.logger.info('Client connected')

@socketio.on('disconnect', namespace='/')
def test_disconnect():
  app.logger.info('Client disconnected')

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
  app.logger.error(f'An error occurred: {e}')

def background_data_update():
  while True:
    try:
      global data
      data = load_data()  # データをリロード
      app.logger.info("Sending update_all: %s", data["devices"])
      socketio.emit(
          "update_all", {"devices": data["devices"]}, namespace='/')
    except json.JSONDecodeError:
      app.logger.error("JSON decode error, skipping this iteration")
    socketio.sleep(1)

if __name__ == '__main__':
  app.debug = True  # デバッグモードを有効にする
  socketio.start_background_task(target=background_data_update)
  socketio.run(app, host='0.0.0.0', port=5000, ssl_context=context)
