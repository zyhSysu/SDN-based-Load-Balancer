#!/usr/bin/python
"""
The program installs a load balancer on pox controller.
In this program we create a simple datacenter topology, like this:
							
							task simulator
								   |
								   |
							gateway switch
								   |
								   |
							 load balancer
						   /			  \
						  /				   \
				  internal switch   internal switch
						 |					|
						 |					|
					  server			  server

Everytime a new host try to request a service, the load balancer
will find a server with lightest load and direct the request flow
to that server.
"""

from mininet.net import Mininet 
from mininet.node import Controller 
from mininet.topo import SingleSwitchTopo 
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import TCLink
from package.dctopo import DCTopo
import os
import sys
 
class Balancer (Controller):
 
	"Custom Controller class to invoke POX forwarding.l2_learning"
	def start (self): 

		"Start POX learning switch" 
		self.pox = '%s/pox/pox.py' % os.environ['HOME'] 
		self.cmd(self.pox, 'balancer &')
 
	def stop (self):
 
		"Stop POX" 
		self.cmd('kill %' + self.pox) 

controllers = {'balancer': Balancer}

if __name__ == '__main__':
 
	switchNum = 4

	if(len(sys.argv) > 1):
		switchNum = sys.argv[1]

	setLogLevel('info') 
	net = Mininet(topo=DCTopo(switchNum), controller=Balancer, link=TCLink, autoSetMacs=True) 
	net.start() 
#	net.pingAll()
#	net.get('c0').pexec('bash utility/fileOperation.sh all null')
#	CLI(net, script = utility/resetInfo)
	net.get('c0').pexec('bash utility/resetInfo.sh %s' % switchNum)
#	net.pingAll()
	CLI(net)
	net.stop() 
