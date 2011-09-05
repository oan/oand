class Heartbeat():
  pass


class NodeInterface():
  def join(self, server):
    server.connect()
    self.nodeList = server.getNodeList()
    self.nodeList.add(self)
    doHeartBeat()

  def getNodeList():
    return self.nodeList

  def addNode(self, node):
    self.nodelist.add(node);

  def doHeartBeat(self):
    for node in self.nodeList:
      if (node.areYouAlive(self.nodeList, deadList)):
        return true
      else
        self.deadList.add(node)

  def areYouAlive(self, nodeList, deadList):
    if (self.nodeList == nodeList AND self.deadList == deadList AND lessThenFiveMinutesSinceLastHeartBeat()):
      self.nodeList.merge(nodeList)
      self.nodeList.remove(deadList)
      self.deadList.merge(deadList)
    else:
      self.nodeList.merge(nodeList)
      self.nodeList.remove(deadList)
      self.deadList.merge(deadList)
      fork(doHeartBeat())
    return True

solServer = NodeInterface()
aspServer = NodeInterface()

mpLaptop = NodeInterface()

mpLaptop.join(solServer)
reqisterTimer(mpLaptop.doHeartBeat, 5)


class NodeStat:
  lastOnline = "110101"
  online = True
