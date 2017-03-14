#! /usr/bin/env/ python
from sys import argv

import lidapy
from lidapy import LIDAThread, Config


blank_position = lidapy.Topic('oxplayer/blank')
action_topic = lidapy.Topic('oxplayer/env/action')


def see_board():
    msg = blank_position.receive(timeout=1)
    if msg:
        lidapy.loginfo(msg)
        lidapy.loginfo("motor move:"+str(msg))
        action_topic.send(int(msg)+1)


lidapy.init(config=Config(argv[1]), process_name='sensory_motor_memory')
LIDAThread(name='sensory_motor_memory', callback=see_board).start()
