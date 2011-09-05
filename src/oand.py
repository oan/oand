#!/usr/bin/env python
'''
Test of DHT algorithms.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We own it all"
__version__ = "0.1"
__status__ = "Test"

from abc import ABCMeta, abstractmethod

class Config():
  def __init__(self, serverName):
    self.serverName = serverName

  def getServerName(self):
    return self.serverName

class NetworkNode():
  __metaclass__ = ABCMeta

  config = None
  
  def __init__(self, config):
    self.config = config

  @abstractmethod
  def join(self, node):
    pass

  @abstractmethod
  def addNode(self, networkNode):
    pass

class CircularNetworkNode(NetworkNode):
  prevNode = None
  nextNode = None

  def join(self, oandNode):    
    oandNode.addNode(self)

  def addNode(self, networkNode):
    if (self.prevNode == None and self.nextNode == None):
      self.nextNode = networkNode
      self.prevNode = networkNode
      oldPrevNode = networkNode
    elif self.prevNode != networkNode:
      oldPrevNode = self.prevNode
      self.prevNode.setNextNode(networkNode)
      self.prevNode = networkNode

    networkNode.setPrevNode(oldPrevNode)
    networkNode.setNextNode(self)

  def setPrevNode(self, networkNode):
    self.prevNode = networkNode

  def setNextNode(self, networkNode):
    self.nextNode = networkNode

  def dbgWalk(self, startNode = None):      
    if (startNode != self):
      if (startNode == None):
        startNode = self
      else:
        print self.config.getServerName()
      if (self.nextNode):
        self.nextNode.dbgWalk(startNode)
      else:
        print "None"

class OAND():
  networkNode = None
  config = None

  def __init__(self, networkNode, config, firstFriendNode = None):
    self.networkNode = networkNode(config)
    self.config = config
    
    if (firstFriendNode != None):
      self.join(firstFriendNode)

  def startDeamon(self):
    self.dbgPrintNetwork()

  def join(self, oandNode):
    print "Connect " + self.config.getServerName() + " with " + oandNode.config.getServerName()
    self.networkNode.join(oandNode)

  def addNode(self, networkNode):
    self.networkNode.addNode(networkNode)

  def dbgPrintNetwork(self):
    print "Nodes in network on " + self.config.serverName
    self.networkNode.dbgWalk()
    print

def buildNetwork(networkNode):
  # Simulate starting of 4 nodes, on 4 different physical machines
  solServer = OAND(networkNode, Config('solServer'))
  solServer.startDeamon()

  mapaBook = OAND(networkNode, Config('mapaBook'), solServer)
  mapaBook.startDeamon()

  aspServer = OAND(networkNode,  Config('aspServer'), solServer)
  aspServer.startDeamon()

  daliBook = OAND(networkNode,  Config('daliBook'), aspServer)
  daliBook.startDeamon()

  solServer.dbgPrintNetwork()

if __name__ == '__main__':
  buildNetwork(CircularNetworkNode)