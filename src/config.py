#!/usr/bin/env python
'''
Holding all configurations that can be done to oand.

Usually reading contents from a config file (oand.conf) but also possible
to initialize all data via the constructor.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Amivono AB"
__maintainer__ = "daniel.lindh@cybercow.se"
__license__ = "We pwn it all."
__version__ = "0.1"
__status__ = "Test"

import ConfigParser

class Config():
  # The name of the server oand is running on. This has no connection
  # to the hostname in the OS.
  _serverName = None

  # The ip number or domain name of this oand node.
  _serverDomainName = None

  # The tcp/ip port that is open for connection.
  _serverPort = None

  # Best Friend Forever Node. The first node to connect to, which will
  # give you access and knowledge to the whole network.
  _bffNode = None

  def __init__(self, serverName, domainName, port, bffNode = None):
    self._serverName = serverName
    self._serverDomainName = domainName
    self._serverPort = port
    self._bffNode = bffNode

  @classmethod
  def fromFilename(cls, filename):
    "Initialize Config from a file"
    config = ConfigParser.ConfigParser()    
    config.readfp(open(filename))

    return cls(
      config.get("oand", "server-name"),
      config.get("oand", "server-domain-name"),
      config.get("oand", "server-port"),
      config.get("oand", "bff-node")
    )

  def getServerName(self):
    return self._serverName

  def getServerDomainName(self):
    return self._serverDomainName

  def getServerPort(self):
    return self._serverPort

  def getBffNode(self):
    return self._bffNode