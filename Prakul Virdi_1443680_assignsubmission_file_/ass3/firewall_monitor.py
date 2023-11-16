from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.dpid import dpid_to_str
from ryu.lib.packet import ethernet
from ryu.ofproto import ofproto_v1_3_parser

class Controller(RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)

        self.host_to_mac = {
            "h1" : "fe:92:92:55:92:e2",
            "h2" : "ce:85:4e:0e:9c:1f",
            "h3" : "8a:f5:02:99:2b:0b",
            "h4" : "62:b9:81:f8:9a:af",
            "h5" : "ae:99:0d:29:93:42"
        }

        self.learner = {}

        self.firewall_rules = [
            # block (h2, h5)
            (self.host_to_mac["h2"], self.host_to_mac["h5"]),
            (self.host_to_mac["h5"], self.host_to_mac["h2"]),
            # block (h3, h5)
            (self.host_to_mac["h3"], self.host_to_mac["h5"]),
            (self.host_to_mac["h5"], self.host_to_mac["h3"]),
            # block (h1, h4)
            (self.host_to_mac["h1"], self.host_to_mac["h4"]),
            (self.host_to_mac["h4"], self.host_to_mac["h1"])
        ]

        self.h3_to_s1_cnt = 0        

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def features_handler(self, ev):
        '''
        Handshake: Features Request Response Handler

        Installs a low level (0) flow table modification that pushes packets to
        the controller. This acts as a rule for flow-table misses.
        '''
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()

        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.__add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        '''
        Packet In Event Handler

        Takes packets provided by the OpenFlow packet in event structure and
        floods them to all ports. This is the core functionality of the Ethernet
        Hub.
        '''
        msg = ev.msg
        datapath = msg.datapath
        ofproto = msg.datapath.ofproto
        parser = msg.datapath.ofproto_parser
        dpid = msg.datapath.id
        pkt = packet.Packet(msg.data)
        in_port = msg.match['in_port']
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None

        '''
            Learning Switch - 
            check if mac address to port mapping has been learned
        '''
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        if not eth_pkt:
            return

        # self.logger.info("ethertype == {}".format(eth_pkt.ethertype))

        # ignore default packets
        if eth_pkt.ethertype == 34525:
            return

        src_mac = eth_pkt.src
        dst_mac = eth_pkt.dst

        # check firewall rules
        if (src_mac, dst_mac) in self.firewall_rules:
            self.logger.info("communication blocked between {}".format((src_mac,dst_mac)))
            actions = []
            match = datapath.ofproto_parser.OFPMatch(eth_dst=dst_mac,eth_src=src_mac)
            self.__add_flow(datapath, 2, match, actions=actions)
            out = parser.OFPPacketOut(datapath=datapath,buffer_id=msg.buffer_id,in_port=in_port,actions=actions,data=data)
            datapath.send_msg(out)
            return

        # if packet from h3 arrives at s1, increment count
        if dpid_to_str(datapath.id) == "0000000000000001" and src_mac == self.host_to_mac["h3"]:
            self.h3_to_s1_cnt += 1
            self.logger.info("Packet arrived from h3 at s1, total count = {}".format(self.h3_to_s1_cnt))

            if not self.added:
                match = datapath.ofproto_parser.OFPMatch(in_port=in_port,eth_src=src_mac)
                if dst_mac == self.host_to_mac["h5"]:
                    self.__add_flow(datapath, 3, match, actions=[])
                else:
                    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
                    self.__add_flow(datapath, 3, match, actions=actions)
                self.added = True
                self.logger.info("installed rules for counting!")

        # learning switch
        if dpid_to_str(datapath.id) not in self.learner:
            self.learner[dpid_to_str(datapath.id)] = {}

        if src_mac not in self.learner[dpid_to_str(datapath.id)]:
            self.logger.info("Learning! source mac : {} is at port number {}".format(src_mac,in_port))
            self.learner[dpid_to_str(datapath.id)][eth_pkt.src] = in_port

        if dst_mac in self.learner[dpid_to_str(datapath.id)]:
            out_port = self.learner[dpid_to_str(datapath.id)][dst_mac]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
            self.__add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
        return

    def __add_flow(self, datapath, priority, match, actions):
        '''
        Install Flow Table Modification

        Takes a set of OpenFlow Actions and a OpenFlow Packet Match and creates
        the corresponding Flow-Mod. This is then installed to a given datapath
        at a given priority.
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        self.logger.info("Flow-Mod written to {}".format(dpid_to_str(datapath.id)))
        datapath.send_msg(mod)