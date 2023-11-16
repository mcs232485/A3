###########################################################
#######  Student Name Avishek Mukhopadhyay                #
#######  Entry Number 2021MCS2125                         #
#######  Assignment   3                                   #
###########################################################

import time
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import RemoteController
from time import sleep
from mininet.node import OVSSwitch
from mininet.log import setLogLevel
from mininet.node import Controller



###########################################################
#######  Class Name  MyAssignmentNetwork                  #
#######  Purpose Implementation of given network          #
###########################################################
class MyAssignmentNetwork(Topo):
   def build(self):
       # add 2 switches to the network
       switch1    = self.addSwitch('switch1')
       switch2  = self.addSwitch('switch2')
       # add 5 hosts  to the network along with mac address, ip and name
       host1   = self.addHost('host1', mac="00:00:00:00:10:11", ip="10.0.0.1/24"  )
       host2= self.addHost('host2', mac="00:00:00:00:10:12", ip="10.0.0.2/24"  )
       host3  = self.addHost('host3', mac="00:00:00:00:10:13", ip="10.0.0.3/24"  )
       host4 = self.addHost('host4', mac="00:00:00:00:10:14",   ip="10.0.0.4/24" )
       host5 = self.addHost('host5',   mac="00:00:00:00:10:15", ip="10.0.0.5/24"  )
       # add link to prepare the network
       self.addLink(host1,switch1)
       self.addLink(host2,switch1)
       self.addLink(host3,switch1)
       self.addLink(switch1,switch2)
       self.addLink(host4,switch2)
       self.addLink(host5,switch2)

if __name__== '__main__':
       mysettingnetwork=  MyAssignmentNetwork()
       # Conenct to remote network
       mymain= RemoteController('Remote1', ip = '127.0.0.1')
       myweb = Mininet(topo=mysettingnetwork , controller= mymain )
       setLogLevel('info')
       myweb.start()
       print("Starting My Network....")
       sleep(3)
       #print("Running PINGALL ....")
       # Running Ping all among all
       #myweb.pingAll()
       hos1 = myweb.get('host1')  
       ping_command="ping  -i 0.5 -c 5 10.0.0.2  > ping.txt" 
       print(ping_command)

      
       popen=hos1.popen(ping_command,    shell=True)
       sleep(10)
       print("Running PINGALL ....")
       # Running Ping all among all
       myweb.pingAll()
       myweb.stop()

