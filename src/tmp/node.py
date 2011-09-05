#!/usr/bin/env python
'''
Test of DHT algorithms.

'''

__author__ = "daniel.lindh@cybercow.se"
__copyright__ = "Copyright 2011, Awxire AB"
__maintainer__ = "Daniel Lindh"
__email__ = "daniel@cybercow.se"
__license__ = "???"
__version__ = "0.1"
__status__ = "Test"  

class Node():
  def __init__(self, node_name):
    self.neighbors=list()
    self.data = {}
    self.folder = {}
    self.node_name=node_name
    
  def join(self, node):
    pass

  def add_prev_node(self, node):
    self.neighbors.insert(0, node)
  
  def add_next_node(self, node):
    self.neighbors.append(node)
    
  def set_value(self, key, value):
    self.data[key] = "Owner of the value: " + self.node_name + " Value: " + value
    self.folder[key] = "asdf" + key
    self.replicate(key, value)
            
  def get_value(self, key):
    if (self.data.has_key(key)):
      return self.data[key]
      
    for node in self.neighbors:
      value=node.get_value(key)
      if value != None:
        return value

    return None
  
  def get_folder_list(self, key):
    print "Node key:" + self.node_name
    if (len(self.folder)):
      return self.folder
    
    if (self.folder.has_key(key)):
      return self.folder[key]
      
    for node in self.neighbors:
      value=node.get_ls(key)
      if value != None:
        return value

    return None

  def replicate(self, key, value):
    print "Replicate to node:" + self.node_name
    for node in self.neighbors:
      if (node.data.has_key(key) == False):
        node.add_value(key, value)

class NetworkFactory():
  def build_network():
    pass
  
class CircularNetworkFactory():
  nodes = {}
  
  def build_network(self, num):
    self.nodes[0] = self.make_node("Node 0")
    for i in range(1, num):
      self.nodes[i] = self.make_node("Node " + str(i))
      self.nodes[i-1].add_node(self.nodes[i])
      self.nodes[i].add_node(self.nodes[i-1])
      
    self.nodes[0].add_node(self.nodes[num-1], True)
    self.nodes[num-1].add_node(self.nodes[0])
    
  def make_node(self, name):
    return Node(name)
  
  def get_nodes(self):
    return self.nodes
    
class FriendNetworkFactory():
  def build_network():
    pass

class CentralNodeNetworkFactory():
  def build_network():
    pass

class Network():
  nodes = {}
    
  def build(self, max_nodex):
    pass
    
  def get_node(self, node_id):
    return self.nodes[node_id]
    
if __name__ == '__main__':
  network = Network()
  network.build(100)
  network.build_network(100)
  
  node1 = network_factory.get_nodes()[80]
  node2 = network_factory.get_nodes()[50]
  node3 = network_factory.get_nodes()[99]

  node1.add_value("/iso/ubuntu10.iso", "This is an ubuntu iso.")

  print node2.get_ls("/iso")
  print node2.get_value("/iso/ubuntu10.iso")