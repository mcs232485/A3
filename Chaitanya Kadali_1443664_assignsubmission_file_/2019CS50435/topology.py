from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch, OVSController, RemoteController
from mininet.cli import CLI

class CustomTopology(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add hosts to s1
        h1 = self.addHost('h1', mac = "e0:98:26:2b:a6:a5", ip=("10.0.0.1"))
        h2 = self.addHost('h2', mac = "a6:6e:44:09:9f:1a", ip=("10.0.0.2"))
        h3 = self.addHost('h3', mac = "c9:63:b6:8f:4e:a2", ip=("10.0.0.3"))

        # Add hosts to s2
        h4 = self.addHost('h4', mac = "e4:f8:79:ed:0d:c3", ip=("10.0.0.8"))
        h5 = self.addHost('h5', mac = "e9:fa:35:45:7c:6d", ip=("10.0.0.8"))

        # Connect hosts to switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s2)
        self.addLink(h5, s2)

        # Connect switches together
        self.addLink(s1, s2)

def main():
    # Create a Mininet instance with the custom topology and use the reference controller
    topo = CustomTopology()
    net = Mininet(topo=topo, controller=RemoteController)

    # Start the network
    net.start()

    # Run the Mininet command line interface
    CLI(net)

    # Clean up and stop the network
    net.stop()

if __name__ == '__main__':
    main()

