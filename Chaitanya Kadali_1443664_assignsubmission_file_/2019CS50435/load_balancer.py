from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from ryu.lib.dpid import dpid_to_str
from ryu.lib.packet.ether_types import ETH_TYPE_IP

class Controller(RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.learner = {}
        self.turn = -1
        self.hm = {
            "h1": "e0:98:26:2b:a6:a5",
            "h2": "a6:6e:44:09:9f:1a",
            "h3": "c9:63:b6:8f:4e:a2",
            "h4": "e4:f8:79:ed:0d:c3",
            "h5": "e9:fa:35:45:7c:6d"
        }
        self.hp = {
            "h1": "10.0.0.1",
            "h2": "10.0.0.2",
            "h3": "10.0.0.3",
            "h4": "10.0.0.42",
            "h5": "10.0.0.42",
        }

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto, parser = datapath.ofproto, datapath.ofproto_parser
        self.logger.info(f"Handshake taken place with {dpid_to_str(datapath.id)}")
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.__add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg, datapath = ev.msg, ev.msg.datapath
        ofproto, parser = datapath.ofproto, datapath.ofproto_parser
        pkt, in_port = packet.Packet(msg.data), msg.match['in_port']
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        if not eth_pkt or eth_pkt.ethertype == ETH_TYPE_IP:
            return

        dpid = dpid_to_str(datapath.id)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)

        if ip_pkt and ip_pkt.dst == "10.0.0.42" and dpid == "0000000000000001":
            if self.turn == -1:
                self.logger.info("setting up round robin rules at switch 1")
                actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
                for host_name, host_ip in self.hp.items():
                    match = parser.OFPMatch(eth_type=0x0800, ipv4_src=host_ip, ipv4_dst="10.0.0.42")
                    self.__add_flow(datapath, 2, match, actions=actions)
                self.turn = 0

            dst_mac = self.hm[f"h{4 if self.turn == 0 else 5}"]
            self.turn = 1 - self.turn

        src_mac, dst_mac = eth_pkt.src, eth_pkt.dst
        if dpid not in self.learner:
            self.learner[dpid] = {}
        if src_mac not in self.learner[dpid]:
            self.learner[dpid][src_mac] = in_port
        out_port = self.learner[dpid].get(dst_mac, ofproto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
            self.__add_flow(datapath, 1, match, actions)
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def __add_flow(self, datapath, priority, match, actions):
        ofproto, parser = datapath.ofproto, datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        self.logger.info(f"Flow-Mod written to {dpid_to_str(datapath.id)}")
        datapath.send_msg(mod)

