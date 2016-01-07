"""
This is a module to perform as a load balancer in the datacenter
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
import time
import os

log = core.getLogger()

IDLE_TIMEOUT = 2 # in seconds
HARD_TIMEOUT = 0 # infinity
OFPFF_SEND_FLOW_REM = 1

LOAD_BALANCER_IP = IPAddr('10.0.0.254')
LOAD_BALANCER_MAC = EthAddr('00:00:00:00:00:FE')

class LoadBalancer (EventMixin):

  class Server:
    def __init__ (self, ip, mac, port):
      self.ip = IPAddr(ip)
      self.mac = EthAddr(mac)
      self.port = port

    def __str__(self):
      return','.join([str(self.ip), str(self.mac), str(self.port)])

  def __init__ (self, connection):
    self.connection = connection
    self.listenTo(connection)
    # Initialize the server list
    self.servers = [
      self.Server('10.0.0.1', '00:00:00:00:00:01', 1),
      self.Server('10.0.0.2', '00:00:00:00:00:02', 2)]
#    self.last_server = 0

#  def get_next_server (self):
    # Round-robin load the servers
#    self.last_server = (self.last_server + 1) % len(self.servers)
#    return self.servers[self.last_server]

  def get_next_server (self):
    #find the server witch lighest work load
    serverMac = os.popen('sudo bash /home/mininet/SDNCompetition/utility/serverSelector.sh').readlines()
    mac_dst = serverMac[0][0:len(serverMac[0])-1]

    os.system('sudo bash /home/mininet/SDNCompetition/utility/fileOperation.sh %s increase' %(mac_dst))

    if (mac_dst == '00:00:00:00:00:01'):
       return self.servers[0]
    else:
       return self.servers[1]

  def handle_arp (self, packet, in_port):

    # Get the ARP request from packet
    arp_req = packet.next

    # Create ARP reply
    arp_rep = arp()
    arp_rep.opcode = arp.REPLY
    arp_rep.hwsrc = LOAD_BALANCER_MAC
#    arp_rep.hwdst = arp_req.hwsrc
    arp_rep.hwdst = packet.src
    arp_rep.protosrc = LOAD_BALANCER_IP
    arp_rep.protodst = arp_req.protosrc

    # Create the Ethernet packet
    eth = ethernet()
    eth.type = ethernet.ARP_TYPE
    eth.dst = packet.src
    eth.src = LOAD_BALANCER_MAC
    eth.set_payload(arp_rep)

    # Send the ARP reply to client
    msg = of.ofp_packet_out()
    msg.data = eth.pack()
    msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
    msg.in_port = in_port
    self.connection.send(msg)

  def handle_request (self, packet, event):

    # Get the next server to handle the request
    server = self.get_next_server()

    "First install the reverse rule from server to client"
    msg = of.ofp_flow_mod()
    msg.idle_timeout = IDLE_TIMEOUT
    msg.hard_timeout = HARD_TIMEOUT
    msg.buffer_id = None

    # Set packet matching
    # Match (in_port, src MAC, dst MAC, src IP, dst IP)
    msg.match.in_port = server.port
    msg.match.dl_src = server.mac
#    msg.match.dl_dst = packet.src
#    msg.match.dl_type = ethernet.IP_TYPE
    msg.match.nw_src = server.ip
    msg.match.nw_dst = packet.next.srcip

    # Append actions
    # Set the src IP and MAC to load balancer's
    # Forward the packet to client's port
    msg.actions.append(of.ofp_action_nw_addr.set_src(LOAD_BALANCER_IP))
    msg.actions.append(of.ofp_action_dl_addr.set_src(LOAD_BALANCER_MAC))
    msg.actions.append(of.ofp_action_output(port = event.port))

    self.connection.send(msg)

    "Second install the forward rule from client to server"
    msg = of.ofp_flow_mod()
    msg.idle_timeout = IDLE_TIMEOUT
    msg.hard_timeout = HARD_TIMEOUT
    msg.buffer_id = None
    msg.data = event.ofp # Forward the incoming packet
    msg.flags = OFPFF_SEND_FLOW_REM

    # Set packet matching
    # Match (in_port, MAC src, MAC dst, IP src, IP dst)
    msg.match.in_port = event.port
    msg.match.dl_src = packet.src
#    msg.match.dl_dst = LOAD_BALANCER_MAC
#    msg.match.dl_type = ethernet.IP_TYPE
    msg.match.nw_src = packet.next.srcip
    msg.match.nw_dst = LOAD_BALANCER_IP
    
    # Append actions
    # Set the dst IP and MAC to load balancer's
    # Forward the packet to server's port
    msg.actions.append(of.ofp_action_nw_addr.set_dst(server.ip))
    msg.actions.append(of.ofp_action_dl_addr.set_dst(server.mac))
    msg.actions.append(of.ofp_action_output(port = server.port))

    self.connection.send(msg)

    os.system('sudo bash /home/mininet/SDNCompetition/utility/hostToServer.sh %s %s' % (event.port, server.mac))

    log.info("Installing %s <-> %s" % (packet.next.srcip, server.ip))

  def _handle_PacketIn (self, event):
    packet = event.parse()

    if packet.type == packet.LLDP_TYPE or packet.type == packet.IPV6_TYPE:
      # Drop LLDP packets 
      # Drop IPv6 packets
      # send of command without actions

      msg = of.ofp_packet_out()
      msg.buffer_id = event.ofp.buffer_id
      msg.in_port = event.port
      self.connection.send(msg)

    elif packet.type == packet.ARP_TYPE:
      # Handle ARP request for load balancer

      # Only accept ARP request for load balancer
      if packet.next.protodst != LOAD_BALANCER_IP:
        return

      log.debug("Receive an ARP request")
      self.handle_arp(packet, event.port)

#    elif packet.type == packet.IP_TYPE:
      # Handle client's request
    else:
      # Only accept ARP request for load balancer
      if packet.next.dstip != LOAD_BALANCER_IP:
        return

      log.debug("Receive an IPv4 packet from %s" % packet.next.srcip)
      self.handle_request(packet, event)

  def _handle_FlowStatsReceived (self, event):
    log.info('Host connection down')

    hostOfServer1 = 0
    hostOfServer2 = 0

    for flow in event.stats:
       flow_in_port = flow.match.in_port

       log.info("flow_in_port: %s" % flow_in_port)

       if flow_in_port != 1 and flow_in_port != 2:
          log.info("inside in_port: %s" % flow_in_port)
          server_mac = os.popen('cat /home/mininet/SDNCompetition/hostToServer/%s' % flow_in_port).readlines()
          if server_mac[0][0:len(server_mac[0])-1] == "00:00:00:00:00:01":
             hostOfServer1 += 1
             log.info("server mac: 00:00:00:00:00:01")
          elif server_mac[0][0:len(server_mac[0])-1] == "00:00:00:00:00:02":
             hostOfServer2 += 1
             log.info("server mac: 00:00:00:00:00:02")

    os.system('sudo bash /home/mininet/SDNCompetition/utility/fileOperation.sh %s set %s' % ("00:00:00:00:00:01", hostOfServer1))
    os.system('sudo bash /home/mininet/SDNCompetition/utility/fileOperation.sh %s set %s' % ("00:00:00:00:00:02", hostOfServer2))

  def _handle_FlowRemoved (self, event):
    for con in core.openflow.connections:
       con.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))

class load_balancer (EventMixin):

  def __init__ (self):
    self.listenTo(core.openflow)

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % event.connection)
    LoadBalancer(event.connection)


def launch ():
  # Start load balancer
  core.registerNew(load_balancer)
