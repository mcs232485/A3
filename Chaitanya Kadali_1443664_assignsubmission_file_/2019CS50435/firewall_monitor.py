# -*- coding: utf-8 -*-
from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.dpid import dpid_to_str
from collections import defaultdict

class Controller(RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.book = defaultdict(dict)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        dp, ofp, parser = ev.msg.datapath, ev.msg.datapath.ofproto, ev.msg.datapath.ofproto_parser
        self.__add_flow(dp, 0, parser.OFPMatch(), [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)])
        self.logger.info(f"Handshake with {dpid_to_str(dp.id)}")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg, dp, ofp, parser = ev.msg, ev.msg.datapath, ev.msg.datapath.ofproto, ev.msg.datapath.ofproto_parser
        dpid, pkt, in_port, data = dp.id, packet.Packet(msg.data), msg.match['in_port'], msg.data if msg.buffer_id == ofp.OFP_NO_BUFFER else None
        datapath = dp
        eth_header = pkt.get_protocol(ethernet.ethernet)
        dpid_str = dpid_to_str(datapath.id)
        #self.mac_port_map.setdefault(dpid_str, {})[eth_header.src] = in_port
        if not eth_header:
            return

        if eth_header.ethertype == 34525:
            return

        src = eth_header.src
        dest = eth_header.dst
        rules = [["a6:6e:44:09:9f:1a", "e9:fa:35:45:7c:6d"], ["e9:fa:35:45:7c:6d","a6:6e:44:09:9f:1a"], ["c9:63:b6:8f:4e:a2", "e9:fa:35:45:7c:6d"], ["e9:fa:35:45:7c:6d", "c9:63:b6:8f:4e:a2"], ["e0:98:26:2b:a6:a5", "e4:f8:79:ed:0d:c3"], ["e4:f8:79:ed:0d:c3", "e0:98:26:2b:a6:a5"]]

        if([eth_header.src, eth_header.dst] in rules):
            self.logger.info(f"is it here")
            actions = []
            match = dp.ofproto_parser.OFPMatch(eth_dst = eth_header.dst, eth_src= eth_header.src)
            self.__add_flow(dp, 2, match, actions=actions)
            out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=in_port, actions= actions, data=data)
            dp.send_msg(out)
            return 
        else:
            if(src not in self.book[dpid_str]):
                self.book[dpid_str][src] = in_port

            if(dest in self.book[dpid_str]):
                out_port = self.book[dpid_str][dest]
            else:
                out_port = ofp.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]
            #actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

            if out_port != ofp.OFPP_FLOOD :
                match = datapath.ofproto_parser.OFPMatch(in_port = in_port, eth_dst=dest)
                self.__add_flow(datapath, 3, match, actions)
                
            out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
            self.logger.info("Sending packet out")
            dp.send_msg(out)
            return


    def __add_flow(self, dp, priority, match, actions):
        ofp, parser = dp.ofproto, dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=priority, match=match, instructions=inst)
        self.logger.info(f"Flow-Mod written to {dpid_to_str(dp.id)}")
        dp.send_msg(mod)

