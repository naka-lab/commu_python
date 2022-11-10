# commu_python

CommUとSotaをPythonから制御するためのプログラム．

## CommUのネットワーク接続
- Wifi接続
  - [このページ](https://sota.vstone.co.jp/home/wi-fi_qrcode/)でWifi接続用のQRコードを生成
  - △ボタンと▽ボタンを同時に長押しする
  - 「設定モード〜〜」と発話するので，上ボタンを「QRコード〜〜」と発話するまで押す
  - ○ボタンを押し，最初に生成したQRコードをCommUに見せる
- IPアドレスの確認
  - △ボタンと▽ボタンを同時に長押しする
  - 「設定モード〜〜」と発話するので，上下ボタンを「IPアドレス」と発話するまで押す
  - ○ボタンを押すとIPアドレスをしゃべる
- SSHで接続する（ユーザー名：root，パスワード:edison00）
  ```
  ssh root@192.168.*.*
  ```
- マイクの音量やその他の設定は，Webページ`http://192.168.*.*`から設定可能

## 環境構築
### CommUのセットアップ
- エディタのインストール
  ```
  cd
  wget https://www.nano-editor.org/dist/v6/nano-6.4.tar.gz --no-check-certificate
  tar xvf nano-6.4.tar.gz
  cd nano-6.4
  ./configure
  make
  make install
  ```
- `/home/vstone/lib`に以下の3つのファイルを追加
  ```
  cd /home/vstone/lib
  wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.13.4/jackson-databind-2.13.4.jar
  wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-core/2.13.4/jackson-core-2.13.4.jar
  wget https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-annotations/2.13.4/jackson-annotations-2.13.4.jar
  ```
- 実行用シェルスクリプトを作成
  - `cd`でカレントディレクトリに移動し，`nano run_server.sh`で以下を入力して保存
    - CommUの場合
      ```
      cd commu_python/bin
      chmod +x *.sh
      ./java_run.sh jp/nakalab/Test commu
      ```
    - Sotaの場合
      ```
      cd commu_python/bin
      chmod +x *.sh
      ./java_run.sh jp/nakalab/Test sota
      ```
- 実行権限をつける：`chmod +x run_server.sh`

### Javaプログラムのコンパイル・転送
- [この手順](http://www.vstone.co.jp/sotamanual/index.php?Java%E3%81%A7%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0%E3%82%92%E3%81%97%E3%81%A6%E3%81%BF%E3%82%8B%2F%E6%BA%96%E5%82%99)に従い
環境構築し，このリポジトリをコンパイル・転送する．
- Eclipse 4.6 Neonを使えばMacでも同様の手順で実行可能

## プログラムの作成・実行
### CommU内部PC
- SSHで接続して`./run_server.sh`を実行（wifi接続，IPの確認，SSH接続は前述の「CommUのネットワーク接続」を参照）

### リモートPC
- GUIでCommUを操作するプログラム
  ```
  cd pycommu
  commu_controller.py
  ```
- pythonからCommUを操作するプログラム例（IPは各自の環境に合わせて変更する）
  - CommUの場合：[commu_example.py](python_example/commu_example.py)
  - Sotaの場合：[sota_example.py](python_example/sota_example.py)
- ランダムに動いて発話する関数の使用例（IPは各自の環境に合わせて変更する）：[tts_example.py](python_example/tts_example.py)

## 仕組み
- [ロボット内部で動いているJAVAプログラム](src/jp/nakalab/Test.java)と[リモートPCで動かすPythonプログラム](pycommu/pycommu.py)間でSocket通信でコマンドをやりとりすることでCommUをコントロール
- コマンドとロボットからの戻り値はJson形式（低レイヤのやり取りは[socket_test.py](pycommu/socket_test.py)が分かりやすいかも）
  - 例：
    - リモートPC→ロボット:`{"com":"get_recog_res", "timeout":5000}`（音声認識コマンド）
    - ロボット→リモートPC:`{"result":true, "string":"こんにちは"}`（音声認識結果）
- 実装されてない機能を使いたい場合には，新たなコマンドを定義し，それぞれのプログラムに送受信コードを追加する



