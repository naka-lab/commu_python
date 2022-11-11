import sys
sys.path.append("../pycommu") # このフォルダにパスを通す
import pycommu
import time


def main():
    # ロボットは引数で切り替える
    #commu = pycommu.PyCommu("commu")
    commu = pycommu.PyCommu("sota")

    commu.connect("192.168.1.12")
    commu.enable_torque(False)

    angles = []
    input("Enterを押すと5秒間動きを記録します")
    for i in range(25):
        angles.append( commu.get_pose() )
        time.sleep(0.2)

    input("Enterを押すと記録した動きを再生します")
    commu.enable_torque()
    for i in range(25):
        a = angles[i]
        commu.set_pose(a, range(1,len(a)+1), 200 )
        time.sleep(0.15)

if __name__ == '__main__':
    main()