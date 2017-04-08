#! /usr/bin/env/ python

import lidapy
from lidapy import Config
from lidapy import Task
from lidapy.modules import SensoryMotorMemory
from env.environment import PLAYER1, PLAYER2


blank_position = lidapy.Topic('oxplayer/blank')
action_topic = lidapy.Topic('oxplayer/player2/action')
dorsal_turn_topic = lidapy.Topic('oxplayer/player2/dorsal/turn')

sms = SensoryMotorMemory()
sms.turn = PLAYER1


def make_move():
    msg = blank_position.receive()
    lidapy.loginfo('Received blank_position:'+str(msg))
    lidapy.loginfo('Current turn:'+str(sms.turn))
    if msg is not None and sms.turn == PLAYER2:
        lidapy.loginfo(msg)
        lidapy.loginfo('motor move:'+str(msg))
        action_topic.send(msg)


def receive_turn():
    turn = dorsal_turn_topic.receive()
    lidapy.loginfo('Received turn:'+str(turn))
    if turn:
        sms.turn = int(turn)


agent_config = Config()
agent_config.set_param('rate_in_hz', 1)
lidapy.init(config=agent_config)

sms.tasks.append(Task(name='make_move', callback=make_move))
sms.tasks.append(Task(name='receive_turn', callback=receive_turn))

sms.start()
