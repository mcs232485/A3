from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller
from mininet.cli import CLI

def create_topology():
    net = Mininet(controller=Controller, switch=OVSSwitch)

    # Add a controller
    c0 = net.addController('c0')

    # Add hosts
    h1 = net.addHost('h1', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', mac='00:00:00:00:00:03')
    h4 = net.addHost('h4', mac='00:00:00:00:00:04')
    h5 = net.addHost('h5', mac='00:00:00:00:00:05')

    # Add switches
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    # Link hosts and switches
    net.addLink(h1, s1, port1=1, port2=1)
    net.addLink(h2, s1, port1=2, port2=2)
    net.addLink(h3, s1, port1=3, port2=3)
    net.addLink(h4, s2, port1=1, port2=4)
    net.addLink(h5, s2, port1=2, port2=5)

    # Start the network
    net.start()

    return net

if __name__ == '__main__':
    topology = create_topology()
    CLI(topology)
    topology.stop()

