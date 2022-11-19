# coding: utf8
from __future__ import print_function, unicode_literals
import pycommu
import random
import time

default_pose_commu = [3, -4, 901, 7, -903, -11, 12, -1, 11, -13, -2, 10, -19, 9]
default_pose_sota = [8, -903, -7, 903, -2, 3, -9, 3]

def set_default_pose(commu):
    if commu.get_mode()=="commu":
        default_pose = default_pose_commu
    else:
        default_pose = default_pose_sota
    commu.set_pose( default_pose, list(range(1,len(default_pose)+1)) )

def say_and_move_randomly(commu, content):
    commu.say( content )

    if commu.get_mode()=="commu":
        poses = [
            default_pose_commu,
            [3, -4, -526, -197, 580, 150, -200, -2, 8],
            [3, -4, 517, -190, 580, 150, -200, -2, 300],
            [3, -4, -732, -197, -437, 144, -97, -2, -342],
            [3, -4, -65, 217, 96, -240, -102, -1, -7],
            [3, 363, 634, -97, -633, 178, -102, -1, -7],
            [3, -318, 633, -97, -633, 178, -102, -2, -6],
            [3, 14, 634, -97, -634, 178, -173, -2, -16],
            [3, 14, -596, 22, 583, 80, 193, -2, -9],
        ]
        default_pose = default_pose_commu
    else:
        poses = [
            default_pose_sota,
            [-4, -902, -7, -3, -6, -624, -9, 0],
            [5, -903, -7, -251, 509, -624, -115, 5],
            [2, 33, -564, 22, 614, 50, -128, 7],
            [3, 554, 128, -458, 125, 49, -127, 7],
            [-6, -131, -536, 818, 135, 630, -127, 9],
            [-4, 574, -29, 820, 135, 254, -177, 1],
            [-1, -308, -886, 255, 941, -8, 139, 2],
        ]
        default_pose = default_pose_sota

    n = 0
    while commu.is_speaking():
        if commu.get_mode()=="commu":
            # commuであれば口パクする
            if n%2==0:
                commu.set_pose([550], [14], 100)
            else:
                commu.set_pose([0], [14], 100)

        if n%6==0:
            p = random.choice(poses)
            commu.set_pose( p, list(range(1,len(p)+1)), 1000 )
            commu.wait_for_moving_finished()

        n+=1
        time.sleep(0.1)

    commu.set_pose( default_pose, list(range(1,len(default_pose)+1)) )
    commu.wait_for_moving_finished()

