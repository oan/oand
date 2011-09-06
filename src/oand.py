#!/usr/bin/env python
'''
Proof of concept of distributed nosql database/filesystem.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

from abc import ABCMeta, abstractmethod

from config import Config

class NetworkNode():
  __metaclass__ = ABCMeta

  _config = None
  
  def __init__(self, config):
    self._config = config

  @abstractmethod
  def join(self, node):
    pass

  @abstractmethod
  def addNode(self, networkNode):
    pass

class CircularNetworkNode(NetworkNode):
  prevNode = None
  nextNode = None

  def join(self):
    if (self._config.getBffNode()):
      print "Connect " + self._config.getServerName() + " with " + self._config.getBffNode()._config.getServerName()
      self._config.getBffNode().addNode(self)

      # remoteNode = connect(self_config.getBffNode())
      # remoteNode.addMe(self._config.getServerDomainName(), self._config.getServerPort())

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
        print self._config.getServerName()
      if (self.nextNode):
        self.nextNode.dbgWalk(startNode)
      else:
        print "None"

class OAND():
  _networkNode = None
  _config = None
    
  def startDeamon(self, networkNode, config):
    self._config = config    
    self._networkNode = networkNode(config)
    self.joinOAN()
    self.dbgPrintNetwork()

  def joinOAN(self):    
    self._networkNode.join()

  def addNode(self, networkNode):
    self._networkNode.addNode(networkNode)

  def dbgPrintNetwork(self):
    print "Nodes in network on " + self._config.getServerName()
    self._networkNode.dbgWalk()
    print

def buildNetwork(networkNode):
  # Simulate starting of 4 nodes, on 4 different physical machines
  solServer = OAND()
  solServer.startDeamon(networkNode, Config('sol-server', "localhost", "4000"))

  mapaBook = OAND()
  mapaBook.startDeamon(networkNode, Config('mapa-book', "localhost", "4001", solServer)) # localhost:4000

  aspServer = OAND()
  aspServer.startDeamon(networkNode,  Config('asp-server', "localhost", "4002", solServer)) # localhost:4000

  daliBook = OAND()
  daliBook.startDeamon(networkNode,  Config('dali-book', "localhost", "4003", aspServer)) # localhost:4002

  solServer.dbgPrintNetwork()

if __name__ == '__main__':
  buildNetwork(CircularNetworkNode)