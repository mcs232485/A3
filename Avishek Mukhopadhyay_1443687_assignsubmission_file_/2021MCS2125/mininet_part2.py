import time
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import RemoteController
from time import sleep
from mininet.node import OVSSwitch
from mininet.log import setLogLevel
from mininet.node import Controller

class MyAssignmentNetwork(Topo):
   def build(self):
       switch1    = self.addSwitch('switch1')
       switch2  = self.addSwitch('switch2')
       host1   = self.addHost('host1', mac="00:00:00:00:10:11", ip="10.0.0.1/24")
       host2= self.addHost('host2', mac="00:00:00:00:10:12", ip="10.0.0.2/24")
       host3  = self.addHost('host3', mac="00:00:00:00:10:13", ip="10.0.0.3/24")
       host4 = self.addHost('host4', mac="00:00:00:00:10:14",   ip="10.0.0.4/24")
       host5 = self.addHost('host5',   mac="00:00:00:00:10:15", ip="10.0.0.5/24")
       self.addLink(host1,switch1)
       self.addLink(host2,switch1)
       self.addLink(host3,switch1)
       self.addLink(switch1,switch2)
       self.addLink(host4,switch2)
       self.addLink(host5,switch2)

if __name__== '__main__':
       mysettingnetwork=  MyAssignmentNetwork()
       mymain= RemoteController('Remote1', ip = '127.0.0.1')
       myweb = Mininet(topo=mysettingnetwork , controller= mymain )
       setLogLevel('info')
       myweb.start()
       print("Starting My Network....")
       sleep(3)
       print("Running Ping from host1 ....")
       host1 = myweb.get('host1')  
       ping_command="ping  -i 0.5 -c 5 10.0.0.2 > ping2.txt" 
       print(ping_command)

      
       popen=host1.popen(ping_command,    shell=True)
       sleep(10)

       print("Running Ping from host2 ....")
       host2 = myweb.get('host2')  
       ping_command="ping  -i 0.5 -c 5 10.0.0.5  >> ping2.txt"
       print(ping_command)
       popen=host2.popen(ping_command,    shell=True)
       sleep(20)
       print("Running PINGALL ....")
       # Running Ping all among all
       myweb.pingAll()
       myweb.stop()

