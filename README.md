# QRmanager
![Image](https://github.com/user-attachments/assets/d1a2387b-4d23-4277-9460-d1ac92c09c18)


このアプリは、デバイスに事前につけられているQRコードを読み取り、管理するアプリです。
このアプリではQRコードの読み取り、デバイスが貸し出し中か返却されているかを記憶、デバイスの登録、貸し出し中のデバイスの一覧などができます。
QRコードの読み取りにはOpencv、全体的なGUIにはpyside6を使用しています。
このアプリには同時にスマホ(ブラウザ)用がセットでついてきており、こちらでもQRコードの読み取り、デバイスが貸し出し中か返却されているかを記憶、デバイスの登録、貸し出し中のデバイスの一覧ができます。
また、スマホ(ブラウザ)版では貸し出し時の写真を閲覧することができ、誰が借りたか分かるようになっています。
# 製作時間・時期
25025年2月上旬
20時間程度
# 機能
## 据え置き版(メイン)
1. QRコードの読み取り
2. デバイスの貸し出し、返却ステータスの変更
3. 貸し出し中デバイスの一覧
4. デバイスの一覧
5. デバイスの追加
6. スマホ(ブラウザ)版のサーバ機能
## スマホ(ブラウザ)版 (サブ)
1. QRコードの読み取り
2. デバイスの貸し出し、返却ステータスの変更
3. デバイスのステータス一覧
4. 貸し出し時の画像一覧

# 動作要項
- windows OS(Linuxでも使用できますが、プログラムを少し変更する必要があります)
- python 3.10以上
- ``requirements.txt``に記載されているライブラリが全てインストールされていること
# 初期準備
このアプリではサーバとブラウザとの通信をsslで暗号化しています。スマホ(ブラウザ)版も動作させるなら自己署名証明書と秘密鍵を作成し、``pages\key``に入れてください。
ファイル名は``server.crt``と``server.key``です。
# ライセンス
このアプリケーションは GNU Lesser General Public License v3.0 のもとで公開されています。詳細は LICENSE.txt ファイルを参照してください。 このアプリケーションは PySide6 を利用しています。PySide6 は LGPL v3 ライセンスの下で公開されています。詳細は https://www.qt.io/qt-licensing を参照してください。

BGM by OtoLogic(CC BY 4.0)

# 操作イメージ&動作風景
![Image](https://github.com/user-attachments/assets/ab8e26de-79cf-472a-b130-0c6ece5fe0d2)
ろぼっと倶楽部でバッテリー管理アプリとして実用化しています

![Image](https://github.com/user-attachments/assets/79adadc2-af2c-4094-b4ec-64c5a690eb85)

スマホ版

![Image](https://github.com/user-attachments/assets/185970a7-436a-4a88-abf3-4dc736577f23)
