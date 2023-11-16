import sys

import collections 
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping
from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.dpid import dpid_to_str
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types


class Controller(RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.packet_count = {}  # Dictionary to store packet counts

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.logger.info("Handshake taken place with {}".format(dpid_to_str(datapath.id)))
        self.__add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = msg.datapath.ofproto
        parser = msg.datapath.ofproto_parser
        dpid = msg.datapath.id
        pkt = packet.Packet(msg.data)
        in_port = msg.match['in_port']
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None

        # Extract source and destination MAC addresses from the packet
        eth_dst = pkt.get_protocols(ethernet.ethernet)[0].dst
        eth_src = pkt.get_protocols(ethernet.ethernet)[0].src

        # Define the MAC addresses of Hosts H2, H3, H5, H1, and H4
        mac_h2 = "00:00:00:00:00:02"
        mac_h3 = "00:00:00:00:00:03"
        mac_h5 = "00:00:00:00:00:05"
        mac_h1 = "00:00:00:00:00:01"
        mac_h4 = "00:00:00:00:00:04"

        if dpid == 1:
            # For Switch S1
            if eth_src == "00:00:00:00:00:03":
                # Count packets coming from H3 on Switch S1
                src_mac = eth_src
                if src_mac not in self.packet_count:
                    self.packet_count[src_mac] = 1
                else:
                    self.packet_count[src_mac] += 1
                self.logger.info("Counting packet from H3 on Switch S1. Total packets: {}".format(self.packet_count[src_mac]))


        # Block communication between H2 and H3 with H5, and H1 with H4
        if ((eth_src == mac_h2 and eth_dst == mac_h3) or
            (eth_src == mac_h3 and eth_dst == mac_h2) or
            (eth_src == mac_h3 and eth_dst == mac_h5) or
            (eth_src == mac_h5 and eth_dst == mac_h3) or
            (eth_src == mac_h1 and eth_dst == mac_h4) or
            (eth_src == mac_h4 and eth_dst == mac_h1)):
            self.logger.info("Blocking communication between hosts")
            return
        else:
            # Allow communication for all other hosts
            actions = [datapath.ofproto_parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
            self.logger.info("Sending packet out")
            datapath.send_msg(out)
            return


    def __add_flow(self, datapath, priority, match, actions):

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        self.logger.info("Flow-Mod written to {}".format(dpid_to_str(datapath.id)))
        datapath.send_msg(mod)