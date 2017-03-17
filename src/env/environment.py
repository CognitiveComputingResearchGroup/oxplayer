#!/usr/bin/python
#  coding=utf-8
from functools import partial


import lidapy
from std_msgs.msg import String


# Topic definitions
board_state_topic = lidapy.Topic('oxplayer/env/board', msg_type=String)
action_topic = lidapy.Topic('oxplayer/env/action', msg_type=String)

def first_blank(board):
    for i in range(len(board)):
        if board[i] is -1:
            break
    return i



class OXPlayerEnvironment(object):

    _board = [-1]*9
    _agent_turn = False
    _opponent = partial(first_blank, board=_board)

    def __init__(self, **kwargs):
        self._start = True
        lidapy.init(process_name='Environment')
        self.mainloop()

    def board_string(self):
        board_template = "{}│{}│{}\n" \
                         "─┼─┼─\n" \
                         "{}│{}│{}\n" \
                         "─┼─┼─\n" \
                         "{}│{}│{}\n"
        board_marks = {1:"X", 0:"O", -1:" "}
        ox_board = (board_marks[mark] for mark in self._board)
        return board_template.format(*ox_board)

    def _reset_board(self):
        _board = [-1]*9
        _agent_turn = False

    def receive_move(self):
        msg = action_topic.receive(timeout=1)
        move = -1
        if msg:
            lidapy.loginfo("Env recvd:"+msg)
            move = int(msg)
        return move

    def mainloop(self):
        while True:
            if not self._agent_turn:
                self._board[self._opponent()] = 1
                lidapy.loginfo("Opponent played")
                self._agent_turn = not self._agent_turn
            else:
                move = self.receive_move()
                if move is not -1:
                    lidapy.loginfo("Player plays")
                    self._board[move] = 0
                    self._agent_turn = not self._agent_turn

            lidapy.loginfo(self.board_string())
            board_state_topic.send(self._board)
            print("running")


