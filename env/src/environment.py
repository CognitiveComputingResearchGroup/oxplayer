# coding=utf-8
from time import sleep
from functools import partial

from numpy import average

import lidapy
from std_msgs.msg import String


# Topic definitions
board_state_topic = lidapy.Topic("/oxplayer/env/board", msg_type=String)
action_topic = lidapy.Topic("/oxplayer/env/action", msg_type=String)

def opponent(board):
    for i in range(len(board)):
        if board[i] is -1:
            break
    return i



class OXPlayerEnvironment(object):

    _board = [-1]*9
    _agent_turn = False
    _opponent = partial(opponent, board=_board)

    def __init__(self, **kwargs):
        self._start = True
        lidapy.init(process_names='Environment')

    def board_string(self):
        board_template = "{}│{}│{}\n" \
                         "─┼─┼─\n" \
                         "{}│{}│{}\n" \
                         "─┼─┼─\n" \
                         "{}│{}│{}\n"
        board_marks = {1:"X", 0:"O", -1:" "}
        ox_board = (board_marks[mark] for mark in self._board)
        return board_template.format(*ox_board)

    def call(self):
        if not self._agent_turn:
            self._board[self._opponent()] = 1
            lidapy.loginfo("Opponent played")
        else:
            self._board[self._opponent()] = 0
            lidapy.loginfo("Player plays")
        lidapy.loginfo(self.board_string())
        board_state_topic.send(self._board)

