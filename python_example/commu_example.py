import sys
sys.path.append("../pycommu") # このフォルダにパスを通す
import pycommu

def main():
    commu = pycommu.PyCommu()

    # commuへ接続
    commu.connect("192.168.1.12")

    # 動く
    commu.enable_torque()
    commu.set_pose( [3, -4, 901, 7, -903, -11, 12, -1, 11, -13, -2, 10, -19, 9], list(range(1,15)) )
    commu.wait_for_moving_finished()
    commu.set_pose( [3, -4, -526, -197, 580, 150, 100, -2, 8, -13, -2, 9, -19, 9], list(range(1,15)) )
    commu.wait_for_moving_finished()
    commu.set_pose( [3, -4, 901, 7, -903, -11, 12, -1, 11, -13, -2, 10, -19, 9], list(range(1,15)) )

    # 音声認識待機
    while 1:
        res = commu.wait_for_speech_recognition()
        if res=="こんにちは":
            # 発話
            commu.say( "こんにちは" )
            commu.wait_for_speaking_finished()
            break

    # yes/no発話待機
    while 1:
        commu.say( "終了します．いいですか？" )
        if commu.wait_for_speech_yesno()=="yes":
            break

    

if __name__ == '__main__':
    main()