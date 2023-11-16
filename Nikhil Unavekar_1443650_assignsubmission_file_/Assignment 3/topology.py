from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import RemoteController

class CustomTopology(Topo):
    def build(self):
        # Add left switch (s1) and right switch (s2)
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Connect hosts h1, h2, h3 to switch s1
        h1 = self.addHost("h1", mac="00:00:00:00:00:01")
        h2 = self.addHost("h2", mac="00:00:00:00:00:02")
        h3 = self.addHost("h3", mac="00:00:00:00:00:03")

        self.addLink(s1, h1, cls=TCLink, bw=40, delay='15ms')
        self.addLink(s1, h2, cls=TCLink, bw=40, delay='15ms')
        self.addLink(s1, h3, cls=TCLink, bw=40, delay='15ms')

        # Connect hosts h4, h5 to switch s2
        h4 = self.addHost("h4", mac="00:00:00:00:00:04")
        h5 = self.addHost("h5", mac="00:00:00:00:00:05")

        self.addLink(s2, h4, cls=TCLink, bw=80, delay='35ms')
        self.addLink(s2, h5, cls=TCLink, bw=80, delay='35ms')

        # Connect the two switches
        self.addLink(s1, s2)

controllers = {
    'controller': RemoteController,
}
topos = {
    'customTopology': (lambda: CustomTopology())
}