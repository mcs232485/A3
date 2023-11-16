from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import OVSLink
import sys

from functools import partial

from mininet.net import Mininet
from mininet.node import UserSwitch, OVSKernelSwitch, Controller
from mininet.topo import Topo
from mininet.log import lg, info
from mininet.util import irange, quietRun
from mininet.link import TCLink

class MyTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        h1 = self.addHost('h1', ip="10.0.0.1", mac="00:00:00:00:00:01")
        h2 = self.addHost('h2', ip="10.0.0.2", mac="00:00:00:00:00:02")
        h3 = self.addHost('h3', ip="10.0.0.3", mac="00:00:00:00:00:03")
        h4 = self.addHost('h4', ip="10.0.0.42", mac="00:00:00:00:00:04")
        h5 = self.addHost('h5', ip="10.0.0.42", mac="00:00:00:00:00:05")

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s2)
        self.addLink(h5, s2)
        self.addLink(s1, s2)

# if __name__ == '__main__':
topos = { 'mytopo': ( lambda: MyTopo() ) }
    # topo = MyTopo()
    # net = Mininet(topo=topo, )

