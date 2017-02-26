#!/usr/bin/env python

from lidapy.framework.agent_starter import AgentStarter

from env.src.environment import BasicSensoryMemory, BasicSensoryMotorMemory, TextAttractorWorkspace, TextAttractorProceduralMemory, TextAttractorEnvironment

if __name__ == '__main__':

    try:
        starter = AgentStarter()

        starter.add_module(BasicSensoryMemory)
        starter.add_module(BasicSensoryMotorMemory)
        starter.add_module(TextAttractorWorkspace)
        starter.add_module(TextAttractorProceduralMemory)
        starter.add_module(TextAttractorEnvironment)

        starter.start()

    except Exception as e:
        print "Received an exception: {}".format(e)

    finally:
        pass
