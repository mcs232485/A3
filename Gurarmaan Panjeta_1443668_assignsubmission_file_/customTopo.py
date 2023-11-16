from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink

class CustomTopology(Topo):
    def build(self):
        # Creating Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        # Create Hosts and allocate IPs and MAC addresses
        h1 = self.addHost('h1', mac='00:00:00:00:00:01',  ip='10.0.0.1/24')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02',  ip='10.0.0.2/24')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03',  ip='10.0.0.3/24')
        h4 = self.addHost('h4', mac='00:00:00:00:00:04',  ip='10.0.0.4/24')
        h5 = self.addHost('h5', mac='00:00:00:00:00:05',  ip='10.0.0.5/24')

        # Adding links between switches and hosts
        self.addLink(s1, s2, port1=1, port2=1)
        self.addLink(s1, h1, port1=2, port2=1)
        self.addLink(s1, h2, port1=3, port2=1)
        self.addLink(s1, h3, port1=4, port2=1)
        self.addLink(s2, h4, port1=2, port2=1)
        self.addLink(s2, h5, port1=3, port2=1)

def create_topology():
    topo = CustomTopology()
    net = Mininet(topo=topo, link=TCLink, controller=lambda name: RemoteController(name, ip='127.0.0.1'))
    net.start()
    return net

if __name__ == '__main__':
    net = create_topology()
    net.interact()
    net.stop()
