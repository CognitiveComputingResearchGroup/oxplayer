# coding=utf-8
from time import sleep
from functools import partial

from numpy import average

import lidapy
from std_msgs.msg import String


# Topic definitions
BOARD_STATE_TOPIC = FrameworkTopic("/oxplayer/env/board", String)
ACTION_TOPIC = FrameworkTopic("/oxplayer/env/action", String)

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
            logger.info("Opponent played")
        else:
            self._board[self._opponent()] = 0
            logger.info("Player plays")
        logger.info(self.board_string())
        self.publish(BOARD_STATE_TOPIC,self._board)


class BasicSensoryMemory(SensoryMemory):
    def __init__(self, **kwargs):
        super(BasicSensoryMemory, self).__init__(**kwargs)



    def call(self):
        text = self.get_next_msg(TEXTSCAN_TOPIC)

        logger.info("Recieved {} from topic [{}]".format(text, TEXTSCAN_TOPIC.topic_name))
        if text is not None:
            for x in text.data:
                logger.info("Publishing CognitiveContent({}) to topic [{}]".format(x, DETECTED_FEATURES_TOPIC.topic_name))
                self.publish(DETECTED_FEATURES_TOPIC, CognitiveContent(x))

class TextAttractorWorkspace(Workspace):

    def __init__(self, **kwargs):
        super(TextAttractorWorkspace, self).__init__(**kwargs)
        import collections
        self.nodes = collections.defaultdict(lambda : 0)

    def call(self):
        percept = self.get_next_msg(PERCEPTS_TOPIC)

        if percept is not None:
            logger.info("Recieved {} from topic [{}]".format(percept.value, PERCEPTS_TOPIC.topic_name))
            les = LinearExciteStrategy(.01)
            self.nodes[percept.value]= les.apply(self.nodes[percept.value], 1)

            for key in self.nodes.keys():
                logger.info("{}".format(key))
                logger.info("{0:.2f}".format(self.nodes[key]))

            try:
                coalition = max(self.nodes.iterkeys(), key=lambda k: self.nodes[k])
                logger.info("Max node {}".format(coalition))
            except Exception as e:
                coalition = ''
            finally:
                logger.info("Publishing {} to topic [{}]".format(coalition, WORKSPACE_COALITIONS_TOPIC.topic_name))
                self.publish(WORKSPACE_COALITIONS_TOPIC, CognitiveContent(coalition))

class TextAttractorProceduralMemory(ProceduralMemory):
    SCHEMES = {"a": "an amazing adventure",
               "b": "because birthdays blast",
               "c": "can cats crawl",
               "d": "do dogs dump",
               "e": "every eel etches",
               "f": "forever fumbling farts",
               "g": "got good grammar",
               "h": "how he hops",
               "i": "i in ink",
               "j": "jockies just jam",
               "k": "kittens kill kites",
               "l": "llama legs laugh",
               "m": "moth mates moth",
               "n": "nobody never nags",
               "o": "onward on oocyte",
               "p": "please push pulin",
               "q": "qualms quarry quest",
               "r": "real roasting rant",
               "s": "say something savvy",
               "t": "todd told tales",
               "u": "until uranus usurped",
               "v": "victory vouches valor",
               "w": "wondering wind wallops",
               "x": "x xanthanic xenophobe",
               "y": "yelled yolo yesterday",
               "z": "zen's zero zone"
               }

    def call(self):
        letter = self.get_next_msg(GLOBAL_BROADCAST_TOPIC)
        if letter is not None:
            if letter.value is not None:
                msg = self.config.get_param("procedural_memory", letter.value)
                logger.info("Publishing {} to topic [{}]".format(msg, CANDIDATE_BEHAVIORS_TOPIC.topic_name))
                self.publish(CANDIDATE_BEHAVIORS_TOPIC, msg)


class BasicSensoryMotorMemory(SensoryMotorMemory):
    def __init__(self, **kwargs):
        super(BasicSensoryMotorMemory, self).__init__(**kwargs)
        self.add_publisher(ACTION_TOPIC)

    def add_publishers(self):
        super(BasicSensoryMotorMemory, self).add_publisher(TEXTSCAN_TOPIC)

    def get_next_msg(self, topic):
        return super(SensoryMotorMemory, self).get_next_msg(topic)

    def publish(self, topic, msg):
        super(SensoryMotorMemory, self).publish(topic, msg)

    def call(self):
        behavior = self.get_next_msg(SELECTED_BEHAVIORS_TOPIC)
        self.publish(ACTION_TOPIC, behavior)
