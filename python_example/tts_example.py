import sys
sys.path.append("../pycommu") # このフォルダにパスを通す
import pycommu
import commu_actions

def main():
    # 引数でロボットを切り替える
    commu = pycommu.PyCommu("sota")
    #commu = pycommu.PyCommu("commu")
 
    # commuへ接続
    commu.connect("192.168.1.12")

    # デフォルトのポーズへ移動
    commu_actions.set_default_pose(commu)

    # 動きながらしゃべる
    commu_actions.say_and_move_randomly(commu, "こんにちは．僕の名前はコミューです．よろしくね．")
    

if __name__ == '__main__':
    main()