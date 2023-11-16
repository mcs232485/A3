from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI

class MyTopology(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Create switches
        switch1 = self.addSwitch("s1") 
        switch2 = self.addSwitch("s2") 

        # Create hosts
        host1 = self.addHost("h1", mac="fe:92:92:55:92:e2", ip="10.0.0.1")
        host2 = self.addHost("h2", mac="ce:85:4e:0e:9c:1f", ip="10.0.0.2")
        host3 = self.addHost("h3", mac="8a:f5:02:99:2b:0b", ip="10.0.0.3")
        host4 = self.addHost("h4", mac="62:b9:81:f8:9a:af", ip="10.0.0.42")
        host5 = self.addHost("h5", mac="ae:99:0d:29:93:42", ip="10.0.0.42")

        # Connect hosts to switches
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch1)
        self.addLink(host4, switch2)
        self.addLink(host5, switch2)

        # Connect switches
        self.addLink(switch1, switch2)

def run_mininet():
    topo = MyTopology()
    # use default controller

    # net = Mininet(topo=topo, controller=lambda name: Controller(name, ip='127.0.0.1'))

    # use remote controller
    
    net = Mininet(topo=topo, controller=None)
    controllerIp = '127.0.0.1'
    controllerPort = 6633
    remoteController = RemoteController('c0', ip=controllerIp, port=controllerPort)
    net.addController(remoteController)

    net.start()
    CLI(net)
    net.stop()

if __name__ == "__main__":
    run_mininet()
