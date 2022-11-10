import socket
import json
import time



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.12", 5000))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# socketから改行コードまで読み込む
def read_line( soc ):
    data = b""
    while 1:
        b = soc.recv(1)
        if b==b"\n":
            break
        data += b
    return data.decode("utf-8")


print("----- 動作生成 ------")

command = {
    "com":"servo_on",
}
line = json.dumps(command)+"\n"
s.send(bytes( line, 'utf-8'))
print(read_line(s))

command = {
    "com":"set_pose",
    "ids":[1,2,3,4.5,6,7,8],
    "angles":[0, 0, 0, 0, 0, 0, 0],
    "time":1000
}
line = json.dumps(command)+"\n"
s.send(bytes( line, 'utf-8'))
print(read_line(s))


command = {
    "com":"set_pose",
    "ids":[1,2,3,4.5,6,7,8],
    "angles":[0, -900, 900, 0, 0, 0, 0],
    "time":1000
}
line = json.dumps(command)+"\n"
s.send(bytes( line, 'utf-8'))
print(read_line(s))


command = {
    "com":"set_pose",
    "ids":[8,2,3,5],
    "angles":[20, 700, -200, 200],
    "time":1000
}

line = json.dumps(command)+"\n"
s.send(bytes( line, 'utf-8'))
print(read_line(s))

print("----- 音声認識 ------")
while 1:
    command = {
        "com":"get_recog_res",
        "timeout":5000
    }
    line = json.dumps(command)+"\n"
    s.send(bytes( line, 'utf-8'))
    line = read_line(s)
    status = json.loads(line)
    print(status)

    if "こんにちは" in status["result"]:
        break
    elif status["result"]=="":
        print("timeout")
    time.sleep(0.1)

while 1:
    command = {
        "com":"get_yes_no",
        "timeout":5000
    }
    line = json.dumps(command)+"\n"
    s.send(bytes( line, 'utf-8'))
    line = read_line(s)
    status = json.loads(line)
    print(status)

    if status["result"]=="yes":
        break
    elif status["result"]=="":
        print("timeout")
    time.sleep(0.1)

print("----- 音声合成 ------")
command = {
    "com":"say",
    "content":"こんにちは"
}
line = json.dumps(command)+"\n"
s.send(bytes( line, 'utf-8'))
print(read_line(s))
time.sleep(3)


print("----- サーボOFF・関節角度取得 ------")
command = {
    "com":"servo_off",
}
line = json.dumps(command)+"\n"
s.send(bytes( line, 'utf-8'))
print(read_line(s))

while 1:
    command = {
        "com":"status"
    }
    line = json.dumps(command)+"\n"
    s.send(bytes( line, 'utf-8'))
    data = json.loads( read_line(s) )
    print(data["angles"])
    time.sleep(0.1)