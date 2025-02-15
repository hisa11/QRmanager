from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import cv2
import json
import os
from datetime import datetime
import logging
import ssl

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# SSL証明書と秘密鍵の読み込み
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('server.crt', 'server.key')

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
                    found_device = next(
                        (dev for dev in data["devices"] if dev["ID"] == qr_id), None)
                    if found_device:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # 保存先フォルダがなければ作成
                        os.makedirs("picture", exist_ok=True)
                        picture_filename = f"{qr_id}_{now.replace(':', '-')}.png"
                        picture_path = os.path.join("picture", picture_filename)
                        cv2.imwrite(picture_path, frame)

                        # 状態を切り替え
                        if not found_device.get("borrowed", False):
                            found_device["borrowed"] = True
                            status = "貸出"
                        else:
                            found_device["borrowed"] = False
                            status = "返却"

                        # JSONファイルの更新
                        with open("data.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)

                        socketio.emit(
                            'update', {'status': status, 'device': found_device})
                        return jsonify({"status": status, "device": found_device})
                    else:
                        return jsonify({"status": "未登録", "device": None})
        return jsonify({"status": "エラー", "device": None})
    finally:
        cap.release()

@app.route('/devices', methods=['GET'])
def get_devices():
    return jsonify(data["devices"])

@socketio.on('connect', namespace='/')
def test_connect():
    app.logger.info('Client connected')

@socketio.on('disconnect', namespace='/')
def test_disconnect():
    app.logger.info('Client disconnected')

def background_data_update():
    while True:
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                updated_data = json.load(f)
            app.logger.info("Sending update_all: %s", updated_data["devices"])
            socketio.emit(
                "update_all", {"devices": updated_data["devices"]}, namespace='/')
        except json.JSONDecodeError:
            app.logger.error("JSON decode error, skipping this iteration")
        socketio.sleep(1)

if __name__ == '__main__':
    socketio.start_background_task(target=background_data_update)
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=context)
