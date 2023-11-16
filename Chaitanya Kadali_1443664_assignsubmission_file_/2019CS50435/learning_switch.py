# -*- coding: utf-8 -*-
from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.dpid import dpid_to_str

class Controller(RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.mac_port_map = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        dp, ofp, parser = ev.msg.datapath, ev.msg.datapath.ofproto, ev.msg.datapath.ofproto_parser
        self.__add_flow(dp, 0, parser.OFPMatch(), [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)])
        self.logger.info(f"Handshake with {dpid_to_str(dp.id)}")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg, dp, ofp, parser = ev.msg, ev.msg.datapath, ev.msg.datapath.ofproto, ev.msg.datapath.ofproto_parser
        dpid, pkt, in_port, data = dp.id, packet.Packet(msg.data), msg.match['in_port'], msg.data if msg.buffer_id == ofp.OFP_NO_BUFFER else None
        datapath = ev.msg.datapath
        actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        if eth_header := pkt.get_protocol(ethernet.ethernet):
            dpid_str = dpid_to_str(datapath.id)
            self.mac_port_map.setdefault(dpid_str, {})[eth_header.src] = in_port
            if (port := self.mac_port_map.get(dpid_str, {}).get(eth_header.dst)) is not None:
                actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                match = datapath.ofproto_parser.OFPMatch(eth_dst=eth_header.dst)
                self.__add_flow(datapath, 1, match, actions)

        pkt_out_msg = datapath.ofproto_parser.OFPPacketOut(datapath=datapath, buffer_id=ev.msg.buffer_id, in_port=in_port, actions=actions, data=ev.msg.data)
        datapath.send_msg(pkt_out_msg)

        out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
        self.logger.info("Sending packet out")
        dp.send_msg(out)

    def __add_flow(self, dp, priority, match, actions):
        ofp, parser = dp.ofproto, dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=priority, match=match, instructions=inst)
        self.logger.info(f"Flow-Mod written to {dpid_to_str(dp.id)}")
        dp.send_msg(mod)

