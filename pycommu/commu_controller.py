import tkinter as tk
from tkinter import ttk
import pycommu
import tkinter.simpledialog as simpledialog
import sys
import time

MOTOR_ID_COMMU2SOTA = [None, None, 1, 2, 3, 4, 5, 7, 8, 6, None, None, None, None]

class Move():
    def __init__(self, commu, id, slider):
        self.commu = commu
        self.id = id
        self.slider = slider

    def __call__(self):
        #commu.set_pose([self.slider.get()*10],  [self.id] )

        if commu.get_mode()=="commu":
            commu.set_pose( [self.slider.get()*10], [self.id] )
        else:
            commu.set_pose( [self.slider.get()*10], [MOTOR_ID_COMMU2SOTA[self.id]] )


def make_slider( root_frame, name, from_, to, id, resolution=1 ):
    frame = tk.Frame(root_frame)
    lbl = tk.Label(frame, text=name, width=15)
    lbl.pack(side="left")
    sb = tk.Scale(frame, orient=tk.HORIZONTAL, from_=from_, to=to, resolution=resolution, length=200 )
    sb.pack(side="left")
    btn = tk.Button( frame, text='go', command=Move(commu, id, sb) )
    btn.pack(side="left")
    frame.pack()
    return sb, btn, lbl

def make_contorl_buttons(root_frame, sliders):
    frame = tk.Frame(root_frame)
    tk.Button( frame, text="トルクON", command=lambda :commu.enable_torque() ).pack(side="left")
    tk.Button( frame, text="トルクOFF", command=lambda :commu.enable_torque(False) ).pack(side="left")

    def get_current_angles():
        angles = commu.get_pose()
        for i, a in enumerate(angles):
            if len(angles)==14:
                # commuの場合
                slider_id = i
            else:
                # sotaの場合
                slider_id = MOTOR_ID_COMMU2SOTA.index(i+1)-1
            sliders[slider_id].set(a/10)
        angle_entry.delete(0,tk.END)
        angle_entry.insert(0, "[" + ", ".join([ str(a) for a in angles]) + "]")
    tk.Button( frame, text="現在角度取得", command=get_current_angles ).pack(side="left")

    def set_zero():
        num_motors = 14
        if commu.get_mode()=="sota":
            num_motors = 8
        for s in sliders:
            s.set(0)
        commu.set_pose( [0]*num_motors, list(range(1,num_motors+1)) )
    tk.Button( frame, text="ゼロポーズ", command=set_zero ).pack(side="left")

    def set_default():
        if commu.get_mode()=="commu":
            angles = [0]*14
            angles[2] = -900
            angles[4] = 900
        else:
            angles = [0]*8
            angles[1] = -900
            angles[3] = 900

        for s, a in zip(sliders, angles):
            s.set(a/10)
        commu.set_pose( angles, list(range(1,len(angles)+1)) )
    tk.Button( frame, text="デフォルトポーズ", command=set_default ).pack(side="left")

    frame.pack()

    angle_entry = tk.Entry(root_frame,width=50)
    angle_entry.pack()
    

def main():
    # モード選択
    frame = tk.Frame(root)
    mode = tk.IntVar()

    def mode_changed():
        if mode.get()==0:
             for i in range(len(buttons)):
                buttons[i]["state"] = "normal"
                sliders[i]["state"] = "normal"
                labels[i]["state"] = "normal"           
                commu.set_mode("commu")
        else:
            for i in range(len(buttons)):
                if i==0 or i>8:
                    buttons[i]["state"] = "disable"
                    sliders[i]["state"] = "disable"
                    labels[i]["state"] = "disable"
                commu.set_mode("sota")
    tk.Radiobutton(frame, value=0, variable=mode, text="CommU", command=mode_changed).pack(side="left")
    tk.Radiobutton(frame, value=1, variable=mode, text="Sota", command=mode_changed).pack(side="left")
    frame.pack()


    # 動作コントロール用フレーム
    frame = tk.Frame(root, bd=2, relief="groove")
    names = ["腰ピッチ","腰ヨー","左肩ピッチ","左肩ロールor肘","右肩ピッチ","右肩ロールor肘","頭ピッチ","頭ロール","頭ヨー","目ピッチ","左目ヨー","右目ヨー","まぶた","口"]
    min_max = [(-15,15),(-67,67),(-108,108),(-45,30),(-108,108),(-30,45),(-20,25),(-15,15),(-85,85),(-22,22),(-35,20),(-20,35),(-65,3),(-3,55),]
    sliders = []
    ids = []

    i = 0
    sliders = []
    buttons = []
    labels = []
    for i in range(14):
        s, b, l = make_slider(frame, names[i], min_max[i][0], min_max[i][1], i+1)
        sliders.append(s)
        buttons.append(b)
        labels.append(l)

    make_contorl_buttons( frame, sliders )

    frame.pack()

    # 音声発話用フレーム
    frame = tk.Frame(root, bd=2, relief="groove")
    say_entry = tk.Entry(frame,width=30)
    say_entry.pack(side="left")
    tk.Button( frame, text="発話", command=lambda: commu.say(say_entry.get()) ).pack(side="left")
    tk.Button( frame, text="オンライン音声", command=lambda: commu.enable_openjtalk(False) ).pack(side="left")
    tk.Button( frame, text="オフライン音声", command=lambda: commu.enable_openjtalk(True) ).pack(side="left")
    frame.pack()

    # 顔認識関連
    frame = tk.Frame(root, bd=2, relief="groove")
    face_recog_entry = tk.Entry(frame,width=30)
    face_recog_entry.pack(side="left")
    def face_recog():
        commu.set_pose( [-150,0,0], [7,8,6], 500 )
        commu.enable_face_estimation( True, True, True )
        commu.start_face_detection()
        for i in range(100):
            face_info = commu.get_face_info()

            if face_info["is_detected"]:
                face_recog_entry.delete(0,tk.END)
                face_recog_entry.insert(0, f"名前:{face_info['name']}, 年齢:{face_info['age']}, 性別:{face_info['sex']}, 笑顔度:{face_info['smile_score']}" )
                commu.say("顔検出成功．")
                if face_info["name"]!="":
                    commu.say( face_info["name"] + "さんだね．")
                break
            time.sleep(0.1)
        else:
            commu.say("顔検出失敗")
    tk.Button( frame, text="顔認識", command=face_recog).pack(side="left")
    frame.pack()

    # 顔学習
    frame = tk.Frame(root, bd=2, relief="groove")
    face_learn_entry = tk.Entry(frame,width=30)
    face_learn_entry.insert(0, "名前を入力してください")
    face_learn_entry.pack(side="left")
    def face_learn():
        commu.set_pose( [-150,0,0], [7,8,6], 500 )
        commu.enable_face_estimation( True, True, True )
        commu.start_face_detection()
        for i in range(100):
            face_info = commu.get_face_info()

            if face_info["is_detected"]:
                res = commu.add_user_data( face_learn_entry.get() )["result"]
                if res:
                    commu.say(face_learn_entry.get() + "さんの顔を覚えたよ")
                    break
            time.sleep(0.1)
        else:
            commu.say("顔学習失敗")

    tk.Button( frame, text="顔学習", command=face_learn).pack(side="left")
    tk.Button( frame, text="顔削除", command=lambda: commu.remove_all_user() ).pack(side="left")
    frame.pack()

    root.mainloop()

if __name__=="__main__":
    root = tk.Tk()
    root.title("CommU Controller")

    commu = pycommu.PyCommu()

    ip = simpledialog.askstring('IPアドレス', 'IPアドレスを入力してください', initialvalue="192.168.1.12")

    if ip is None:
        sys.exit()

    commu.connect( ip )
    commu.enable_torque()
    main()
