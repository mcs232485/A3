from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, OVSController
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

# sudo -E python3 custom_topolog.py

# Custom topology class
class CustomTopology(Topo):
    def build(self):
        # Create switches
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')

        # Create hosts
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')
        host5 = self.addHost('h5')

        # Connect hosts to switches
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch1)
        self.addLink(host4, switch2)
        self.addLink(host5, switch2)

        # Connect switches
        self.addLink(switch1, switch2)

# Hub Controller class
class HubController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(HubController, self).__init__(*args, **kwargs)
        self.protocol = 'tcp'  # Add the protocol attribute
        self.IP="127.0.0.1"
        self.port=6651

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Add a table-miss flow entry to flood packets to all ports
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Construct the flow mod message and add it to the switch
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match,
            instructions=inst, table_id=0)
        datapath.send_msg(mod) 

# Main function to create and start the network
def main():
    setLogLevel('info')
    topo = CustomTopology()
    # net = Mininet(topo=topo, controller=HubController)
    net = Mininet(topo=topo, controller=OVSController)
    net.start()

    print("Custom Topology with Hub Controller")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()
