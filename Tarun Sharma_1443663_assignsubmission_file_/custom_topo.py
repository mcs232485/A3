from mininet.topo import Topo
from mininet.net import Mininet

# Create a custom topology
class MyTopology(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        # Add hosts
        h1 = self.addHost('h1',mac='00:00:00:00:00:01')
        h2 = self.addHost('h2',mac='00:00:00:00:00:02')
        h3 = self.addHost('h3',mac='00:00:00:00:00:03')
        h4 = self.addHost('h4',mac='00:00:00:00:00:04')
        h5 = self.addHost('h5',mac='00:00:00:00:00:05')

        # Connect hosts to the switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(s1, s2)
        self.addLink(s2, h4)
        self.addLink(s2, h5)
topos = { 'mytopo' : (lambda : MyTopology() ) }
