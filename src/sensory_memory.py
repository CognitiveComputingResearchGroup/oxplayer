#! /usr/bin/env/ python
from sys import argv

import lidapy
import ast
from lidapy import Config
from lidapy.modules import SensoryMemory
from env.environment import first_blank, PLAYER2, PLAYER1
from lidapy import Task

board_state_topic = lidapy.Topic('oxplayer/env/board')
pain_signal_topic = lidapy.Topic('oxplayer/player2/pain')
blank_position = lidapy.Topic('oxplayer/blank')
turn_topic = lidapy.Topic('oxplayer/env/turn')
dorsal_turn_topic = lidapy.Topic('oxplayer/player2/dorsal/turn')


def see_board():
    board_state = board_state_topic.receive()
    lidapy.loginfo('Received board_state:'+str(board_state))
    if board_state:
        board_state = ast.literal_eval(board_state)
        blank = first_blank(board_state)
        lidapy.loginfo('blank position:'+str(blank))
        blank_position.send(blank)


def dorsal_update():
    turn = turn_topic.receive()
    lidapy.loginfo('Received turn:'+str(turn))
    if turn == PLAYER1 or turn == PLAYER2:
        dorsal_turn_topic.send(turn)
        lidapy.loginfo('Published to '+str(dorsal_turn_topic)+': '+str(turn))


sensory_memory = SensoryMemory()
agent_config = Config()
agent_config.set_param('rate_in_hz', 1)
lidapy.init(config=agent_config)


sensory_memory.tasks.append(Task(name='see_board', callback=see_board))
sensory_memory.tasks.append(Task(name='dorsal_stream', callback=dorsal_update))
sensory_memory.start()
