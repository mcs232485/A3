from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types

class FirewallMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FirewallMonitor, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        # Assuming MAC addresses are known. These would be the actual MAC addresses of H1, H2, H3, H4, H5
        self.firewall_rules = {
            "H2_MAC": ["H5_MAC"],
            "H3_MAC": ["H5_MAC"],
            "H1_MAC": ["H4_MAC"]
        }
        self.h3_packet_count = 0  # Counting packets coming from H3

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        # Same as the LearningSwitch to set up the table-miss flow entry

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        # Same as the LearningSwitch to add a flow entry

    def add_firewall_rule(self, datapath, src, dst):
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_src=src, eth_dst=dst)
        # Empty action list means "drop packet"
        self.add_flow(datapath, 1, match, [])

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Ignore lldp packet
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # Firewall logic
        if src in self.firewall_rules and dst in self.firewall_rules[src]:
            self.logger.info("Dropping packet due to firewall rule: %s -> %s", src, dst)
            return  # Drop the packet

        # Monitoring logic for H3
        if src == "H3_MAC":  # Replace with the actual MAC address of H3
            self.h3_packet_count += 1
            self.logger.info("Packet count from H3: %d", self.h3_packet_count)

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # Learn a MAC address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
