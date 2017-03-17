#! /usr/bin/env/ python
from sys import argv

import lidapy
from lidapy import LIDAThread, Config
from std_msgs.msg import String
from env.environment import first_blank

board_state_topic = lidapy.Topic('oxplayer/env/board')
blank_position = lidapy.Topic('oxplayer/blank', msg_type=String)


def see_board():
    msg = board_state_topic.receive(timeout=1)
    if msg:
        lidapy.loginfo(msg)
        blank = first_blank(msg)
        lidapy.loginfo('blank position:'+str(blank))
        blank_position.send(blank)

lidapy.init(config=Config(argv[1]), process_name='sensory_memory')
LIDAThread(name='sensory_memory', callback=see_board).start()
