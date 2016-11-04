from time import sleep
from functools import partial

from numpy import average

from lidapy.framework.msg import built_in_topics, FrameworkTopic
from lidapy.framework.shared import CognitiveContent
from lidapy.framework.module import FrameworkModule
from lidapy.module.action_selection import ActionSelection
from lidapy.module.current_situational_model import CurrentSituationalModel
from lidapy.module.global_workspace import GlobalWorkspace
from lidapy.module.perceptual_associative_memory import PerceptualAssociativeMemory
from lidapy.module.procedural_memory import ProceduralMemory
from lidapy.module.sensory_memory import SensoryMemory
from lidapy.module.sensory_motor_memory import SensoryMotorMemory
from lidapy.module.workspace import Workspace
from lidapy.framework.strategy import LinearExciteStrategy
from lidapy.util import logger
from std_msgs.msg import String


# Topic definitions
BOARD_STATE_TOPIC = FrameworkTopic("/oxplayer/env/board", String)
ACTION_TOPIC = FrameworkTopic("/oxplayer/env/action", String)
DORSAL_STREAM_TOPIC = built_in_topics["dorsal_stream"]
VENTRAL_STREAM_TOPIC = built_in_topics["ventral_stream"]
DETECTED_FEATURES_TOPIC = built_in_topics["detected_features"]
PERCEPTS_TOPIC = built_in_topics["percepts"]
WORKSPACE_COALITIONS_TOPIC = built_in_topics["workspace_coalitions"]
GLOBAL_BROADCAST_TOPIC = built_in_topics["global_broadcast"]
CANDIDATE_BEHAVIORS_TOPIC = built_in_topics["candidate_behaviors"]
SELECTED_BEHAVIORS_TOPIC = built_in_topics["selected_behaviors"]
NODES_TOPIC = FrameworkTopic("/text_attractor/nodes", String)

ENVIRONMENT_MODULE = "environment"

def opponent(board):
    for i in range(len(board)):
        if board[i] is -1:
            break
    return i



class OXPlayerEnvironment(FrameworkModule):

    _board = [-1]*9
    _turn = False
    _opponent = partial(opponent, board=_board)

    def __init__(self, **kwargs):
        super(OXPlayerEnvironment, self).__init__(ENVIRONMENT_MODULE,**kwargs)
        self.add_publisher(BOARD_STATE_TOPIC)
        self.add_subscriber(ACTION_TOPIC)
        self._start = True


    @classmethod
    def get_module_name(cls):
        return ENVIRONMENT_MODULE

    def display_board(self):
        board = ""
        mark = lambda x: 'X' if self._board[x] is 1 else 'O'
        for pos in range(len(self._board)):
            if pos % 3 is 0:
                board += mark(pos)
            if pos % 3 is 1:
                board += "│"
                board += mark(pos)
                board += "│"
            if pos % 3 is 2:
                board += mark(pos)
                board += "\n"
                if pos % 9 is not 8:
                    board += "─┼─┼─"
                board += "\n"
        return board

    def call(self):
        if not self.turn:
            self._board[self._opponent()] = 1
            logger.info("Opponent plays")
        else:
            self._board[self._opponent()] = 0
            logger.info("Player plays")
        logger.info(self.display_board())


class BasicSensoryMemory(SensoryMemory):
    def __init__(self, **kwargs):
        super(BasicSensoryMemory, self).__init__(**kwargs)

    def add_subscribers(self):
        self.add_subscriber(TEXTSCAN_TOPIC)

    def get_next_msg(self, topic):
        return super(BasicSensoryMemory, self).get_next_msg(topic)

    def publish(self, topic, msg):
        super(BasicSensoryMemory, self).publish(topic, msg)

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
