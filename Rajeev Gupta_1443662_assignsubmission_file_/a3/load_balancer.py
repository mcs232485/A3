from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, arp

class LoadBalancer(app_manager.RyuApp):
    OFP_VERSION = ofproto_v1_3.OFP_VERSION

    def __init__(self, *args, **kwargs):
        super(LoadBalancer, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.server_ports = {4: 1, 5: 2}
        self.client_ports = {1, 2, 3}
        self.server_index = 4  # Start with the first server

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install flow rules to direct traffic to the load balancer
        for client_port in self.client_ports:
            match = parser.OFPMatch(in_port=client_port)
            actions = [parser.OFPActionOutput(self.server_ports[self.server_index])]
            self.add_flow(datapath, 1, match, actions)

            # Round-robin server selection
            self.server_index = 4 if self.server_index == 5 else 5

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)


