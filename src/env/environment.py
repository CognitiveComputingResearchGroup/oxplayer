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
    def __init__(self, **kwargs):
        self._board = [-1] * 9
        self._agent_turn = False
        self._opponent = partial(first_blank, board=self._board)

        lidapy.init(process_name='Environment')
        self.mainloop()

    def board_string(self):
        board_template = '\n' \
                         '{}│{}│{}\n' \
                         '─┼─┼─\n' \
                         '{}│{}│{}\n' \
                         '─┼─┼─\n' \
                         '{}│{}│{}\n'
        board_marks = {1: 'X', 0: 'O', -1: ' '}
        ox_board = (board_marks[mark] for mark in self._board)
        return board_template.format(*ox_board)

    def _is_end(self):
        return -1 not in self._board

    def _reset_board(self):
        for i in range(len(self._board)):
            self._board[i] = -1
        self._agent_turn = False

    @staticmethod
    def receive_action():
        msg = action_topic.receive(timeout=1)
        move = 9
        if msg:
            lidapy.loginfo('Env recvd:' + msg)
            move = int(msg)
        return move

    def _make_move(self, pos, agent_turn):
        if -1 < pos < 9:
            if self._board[pos] == -1:
                mark = int(not agent_turn)
                self._board[pos] = mark
                return True
        return False

    def mainloop(self):
        while True:
            if self._is_end():
                self._reset_board()

            if self._agent_turn:
                move = OXPlayerEnvironment.receive_action()  # receive_action should be bound to an instance
                if move != 9:
                    lidapy.loginfo('Player plays')
            else:
                move = self._opponent()
                lidapy.loginfo('Opponent plays')

            if self._make_move(move, self._agent_turn):
                self._agent_turn = not self._agent_turn

            lidapy.loginfo(self.board_string())
            board_state_topic.send(self._board)
            print('running')
