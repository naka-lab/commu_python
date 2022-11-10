import sys
sys.path.append("../pycommu") # このフォルダにパスを通す
import pycommu
import time

def main():
    commu = pycommu.PyCommu("sota")
    commu.connect("192.168.1.12")

    commu.enable_torque()
    commu.start_face_tracking()

    # 顔認識有効化
    commu.enable_face_estimation( True, True, True )
    
    # 現状の登録されている顔を削除
    commu.remove_all_user()

    detect_cnt = 0
    while 1:
        face_info = commu.get_face_info()
        print(face_info)
        print(detect_cnt)

        if face_info["is_detected"]:
            detect_cnt += 1
        else:
            detect_cnt =0

        if detect_cnt>3:
            if face_info["is_new_user"]:
                #commu.stop_face_tracking()
                commu.say("あなたの名前を教えてください")
                commu.wait_for_speaking_finished()
                name = commu.wait_for_speech_name(10000)
                
                if name=="":
                    commu.say("名前が聞き取れなかったよ")
                    continue

                commu.say( name + "さんだね．覚えるからちょっと待ってね．")
                commu.wait_for_speaking_finished()

                res = commu.add_user_data( name )

                if res["result"]:
                    commu.say( name + "さんのこと，覚えました")
                    commu.say( name + f"さんは{face_info['age']}歳くらいですか？" )
                    commu.wait_for_speaking_finished()
                else:
                    commu.say("ごめんね．覚えられなかった")
                    commu.wait_for_speaking_finished()
                    print("error_code:", res["code"])
                detect_cnt = 0
            else:
                commu.say( face_info["name"] + "さん，こんにちは．")
                commu.wait_for_speaking_finished()
                detect_cnt = 0

        time.sleep(0.1)



if __name__ == '__main__':
    main()