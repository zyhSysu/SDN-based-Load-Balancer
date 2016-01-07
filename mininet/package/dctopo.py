#!/usr/bin/python

"""
Simple datacenter topology

This program builds a simple datacenter topology consisted of k switches and a controller.
The sample topology graph:

							Task simulator
								|
							  switch4
								|
							Flow balancer
						/		|			\
					switch1   switch2    switch3
"""


from mininet.topo import Topo

class DCTopo (Topo):
	"simple datacenter topo"
	
	def __init__ (self, k = 4):
		"create topo"

		# Initialize topology
		Topo.__init__(self)

		self.k = k

		switch = self.addSwitch('s1')

		#Add hosts and switches
		for h in range(1, int(k) + 1):
#			if(h <= 2): 
#				host = self.addHost('h%s' %h, mac='00:00:00:00:00:0%s' %h, ip='10.0.0.%s' %h)
#			else:
#				host = self.addHost('h%s' %h, mac='00:00:00:00:00:0%s' %h, ip='10.0.0.%s' %h)
			host = self.addHost('h%s' % h)
#			switch = self.addSwitch('s%s' % h)

			#if the host stands for server, the network performance should
			#be much better
			linkopts1 = dict(bw=2, delay='1ms', loss=1)
			linkopts2 = dict(bw=0.5, delay='3ms', loss=5)

			#the first host is our simulator
			if(h == 1 or h == 2):
				self.addLink(host, switch, **linkopts1)
			else:
				self.addLink(host, switch, **linkopts2)

#			if(h == 1):
#				gateway = switch
#			else:
#				self.addLink(gateway, switch, **linkopts1)

topos = { 'dctopo': ( lambda: DCTopo() ) }
