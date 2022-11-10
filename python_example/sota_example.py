import sys
sys.path.append("../pycommu") # このフォルダにパスを通す
import pycommu

def main():
    commu = pycommu.PyCommu("sota")

    # commuへ接続
    commu.connect("192.168.1.12")

    # 動く
    commu.enable_torque()
    commu.set_pose( [8, -903, -7, 903, -2, 3, -9, 3], list(range(1,10)) )
    commu.wait_for_moving_finished()
    commu.set_pose( [3, -4, -65, 217, 96, -240, -102, -1, -7], list(range(1,10)) )
    commu.wait_for_moving_finished()
    commu.set_pose( [8, -903, -7, 903, -2, 3, -9, 3], list(range(1,10)) )

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