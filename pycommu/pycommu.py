# coding: utf8
from __future__ import print_function, unicode_literals
import socket
import json
import time

class PyCommu():
    # 関節IDの定義（C_*:Commu, S_:Sota）
    C_BODY_P = 1
    C_BODY_Y = 2
    C_L_SHOULDER_P = 3
    C_L_SHOULDER_R = 4
    C_R_SHOULDER_P = 5
    C_R_SHOULDER_R = 6
    C_HEAD_P = 7
    C_HEAD_R = 8
    C_HEAD_Y = 9
    C_EYE_P = 10
    C_L_EYE_Y = 11
    C_R_EYE_Y = 12
    C_EYELIDs = 13
    C_MOUTH = 14

    S_BODY_Y = 1
    S_L_SHOULDER = 2
    S_L_ELBOW = 3
    S_R_SHOULDER = 4
    S_R_ELBOW = 5
    S_HEAD_Y = 6
    S_HEAD_P = 7
    S_HEAD_R = 8

    def __init__(self, mode="commu"):
        self.set_mode( mode )

    def get_mode(self):
        return self.mode
    
    def set_mode(self, mode):
        if mode!="sota" and mode!="commu":
            print('mode should be "sota" or "commu".')
        self.mode = mode

    def connect(self, ip, port=5000 ):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((ip, 5000))
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def _read_data(self):
        data = b""
        while 1:
            b = self.soc.recv(1)
            if b==b"\n":
                break
            data += b

        return json.loads(data.decode("utf-8"))

    def _send( self, command, content=None, flag=None, angles=None, ids=None, time=None, timeout=None, retry=None, face_smile=None, face_search=None, age_and_sex=None, name=None ):
        data = {}
        data["com"] = command

        if content is not None: data["content"] = content
        if flag is not None: data["flag"] = flag
        if angles is not None: data["angles"] = angles
        if ids is not None: data["ids"] = ids
        if time is not None: data["time"] = time
        if timeout is not None: data["timeout"] = timeout
        if retry is not None: data["retry"] = retry
        if face_smile is not None: data["face_smile"] = face_smile
        if face_search is not None: data["face_search"] = face_search
        if age_and_sex is not None: data["age_and_sex"] = age_and_sex
        if name is not None: data["name"] = name

        line = json.dumps(data)+"\n"
        try:
            self.soc.send(bytes( line, 'utf-8'))
        except TypeError:
            self.soc.send(bytes( line ))

    def say(self, content):
        self._send( "say", content=content )
        return self._read_data()

    def enable_openjtalk(self, enables=True ):
        self._send( "enable_jtalk", flag=enables )
        return self._read_data()

    def enable_torque(self, enables=True):
        if enables:
            self._send("servo_on")
        else:
            self._send("servo_off")
        return self._read_data()

    def set_pose(self,angles, ids, time=1000):
        self._send( "set_pose", angles=list(angles), ids=list(ids), time=time )
        return self._read_data()

    def get_pose(self):
        self._send( "status" )
        return self._read_data()["angles"]

    def get_status(self):
        self._send( "status" )
        return self._read_data()

    def is_speaking(self):
        return self.get_status()["is_speaking"]

    def wait_for_speaking_finished(self):
        while self.is_speaking():
            time.sleep(0.1)

    def is_moving(self):
        return self.get_status()["is_moving"]

    def wait_for_moving_finished(self):
        while self.is_moving():
            time.sleep(0.1)

    def wait_for_speech_recognition(self, timeout=None):
        while 1:
            self._send( "get_recog_res", timeout= timeout if timeout is not None else 5000 )
            res = self._read_data()
            print(res)
            res = res["string"]

            if timeout is not None:
                return res
            elif res!="":
                return res

    def wait_for_speech_yesno(self, timeout=None, retry=5):
        while 1:
            self._send( "get_yes_no", timeout= timeout if timeout is not None else 10000, retry=retry )
            res = self._read_data()
            print(res)
            res = res["string"]

            if timeout is not None:
                return res
            elif res!="":
                return res

    def wait_for_speech_name(self, timeout=None, retry=5):
        while 1:
            self._send( "get_recog_name", timeout= timeout if timeout is not None else 10000, retry=retry )
            res = self._read_data()
            print(res)
            res = res["string"]

            if timeout is not None:
                return res
            elif res!="":
                return res

    def start_face_tracking(self):
        self._send( "start_face_track" )
        return self._read_data()

    def stop_face_tracking(self):
        self._send( "stop_face_track" )
        return self._read_data()

    def start_face_detection(self):
        self._send( "start_face_detect" )
        return self._read_data()

    def stop_face_detection(self):
        self._send( "stop_face_detect" )
        return self._read_data()

    def enable_face_estimation(self, search, smile, age_sex ):
        self._send("enable_face_estimation", face_search=search, face_smile=smile, age_and_sex=age_sex )
        return self._read_data()

    def get_face_info(self):
        self._send( "get_face_info" )
        return self._read_data()

    def add_user_data(self, name):
        self._send( "add_user", name=name )
        res = self._read_data()
 
        if res["result"]==False:
            print("顔登録エラー")
            if res["code"]==-100:
                print("Maybe, I know this face.")
            elif res["code"]==-201:
                print("Out of Range Angle Pitch")
            elif res["code"]==-202:
                print("Out of Range Angle Roll")
            elif res["code"]==-203:
                print("Out of Range Angle Yaw")
            elif res["code"]==-300:
                print("Out of Range Face Size")
            elif res["code"]==-400:
                print("Low FocusScore")
        return res

    def remove_all_user(self):
        self._send("remove_all_user")
        return self._read_data()

    def save_camera_image(self):
        self._send("save_cam_image")
        return self._read_data()


def main():
    commu = PyCommu("sota")
    commu.connect("192.168.1.12")
    commu.enable_openjtalk(True)
    commu.say("テスト")
    commu.wait_for_speaking_finished()

if __name__ == '__main__':
    main()