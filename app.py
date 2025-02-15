from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import cv2
import json
import os
from datetime import datetime
import time

app = Flask(__name__)
socketio = SocketIO(app)

camera_id = 0
qcd = cv2.QRCodeDetector()

# デバイスデータの読み込み
with open("data.json", "r", encoding="utf-8") as f:
  data = json.load(f)

@app.route('/')
def index():
  return render_template('index.html', devices=data["devices"])

@app.route('/scan', methods=['POST'])
def scan_qr():
  cap = cv2.VideoCapture(camera_id)
  ret, frame = cap.read()
  if ret:
    ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
    if ret_qr:
      for s in decoded_info:
        if s:
          qr_id = s
          found_device = next(
              (dev for dev in data["devices"] if dev["ID"] == qr_id), None)
          if found_device:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            picture_path = os.path.join(
                "picture", f"{qr_id}_{now.replace(':', '-')}.png")
            cv2.imwrite(picture_path, frame)
            if not found_device.get("borrowed", False):
              found_device["borrowed"] = True
              status = "貸出"
            else:
              found_device["borrowed"] = False
              status = "返却"
            with open("data.json", "w", encoding="utf-8") as f:
              json.dump(data, f, ensure_ascii=False, indent=4)
            socketio.emit(
                'update', {'status': status, 'device': found_device})
            return jsonify({"status": status, "device": found_device})
          else:
            return jsonify({"status": "未登録", "device": None})
  return jsonify({"status": "エラー", "device": None})

@app.route('/update_status', methods=['POST'])
def update_status():
  content = request.get_json()
  device_id = content.get("id")
  if device_id:
    found_device = next(
        (dev for dev in data["devices"] if dev["ID"] == device_id), None)
    if found_device:
      if found_device.get("borrowed", False):
        found_device["borrowed"] = False
        status = "返却"
      else:
        found_device["borrowed"] = True
        status = "貸出"
      with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
      # サーバー側でステータス変更後、結果を返す
      return jsonify({"status": status, "device": found_device})
    else:
      return jsonify({"status": "未登録", "device": None})
  return jsonify({"status": "エラー", "device": None})

@app.route('/devices', methods=['GET'])
def get_devices():
  return jsonify(data["devices"])

def background_data_update():
  while True:
    with open("data.json", "r", encoding="utf-8") as f:
      updated_data = json.load(f)
    socketio.emit("update_all", {"devices": updated_data["devices"]})
    socketio.sleep(1)  # 1秒ごとに更新送信

if __name__ == '__main__':
  socketio.start_background_task(target=background_data_update)
  socketio.run(app, host='0.0.0.0', port=5000)
