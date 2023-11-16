# Import necessary libraries
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

class LoadBalancerApp(app_manager.RyuApp):
    OFP_VERSION = ofproto_v1_3.OFP_VERSION

    def __init__(self, *args, **kwargs):
        super(LoadBalancerApp, self).__init__(*args, **kwargs)
        self.server_ips = ["10.0.0.4", "10.0.0.5"]
        self.server_index = 0

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # Only handle ARP requests
        if msg.match['eth_type'] == 0x0806:
            # Generate ARP response with the virtual IP's MAC address
            arp_reply = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=[
                    parser.OFPActionOutput(ofproto_v1_3.OFPP_IN_PORT)
                ],
                data=msg.data
            )
            datapath.send_msg(arp_reply)

        # Round-robin server selection for other traffic
        if msg.match['eth_type'] == 0x0800:  # IPv4
            server_ip = self.server_ips[self.server_index]
            self.server_index = (self.server_index + 1) % len(self.server_ips)
            # Add flow rules to forward traffic to the selected server
            actions = [parser.OFPActionSetField(ipv4_dst=server_ip),
                       parser.OFPActionOutput(ofproto_v1_3.OFPP_NORMAL)]
            match = parser.OFPMatch(in_port=in_port, eth_type=0x0800)
            self.add_flow(datapath, 1, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match,
            instructions=inst, table_id=0)
        datapath.send_msg(mod)

# Run the load balancer app
if __name__ == '__main__':
    from ryu.cmd import manager
    manager.main()
