from ryu.base.app_manager import RyuApp
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.dpid import dpid_to_str
from ryu.lib.packet import ethernet, ipv4
from ryu.lib.packet import ether_types

class Controller(RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.learner = {}
        self.turn = -1
        self.host_to_mac = {
            "h1" : "fe:92:92:55:92:e2",
            "h2" : "ce:85:4e:0e:9c:1f",
            "h3" : "8a:f5:02:99:2b:0b",
            "h4" : "62:b9:81:f8:9a:af",
            "h5" : "ae:99:0d:29:93:42"
        }
        self.host_to_ip = {
            "h1" : "10.0.0.1",
            "h2" : "10.0.0.2",
            "h3" : "10.0.0.3",
            "h4" : "10.0.0.42",
            "h5" : "10.0.0.42",
        }

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
        self.logger.info("Handshake taken place with {}".format(dpid_to_str(datapath.id)))
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

        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        if not eth_pkt:
            return

        # ignore default packets
        if eth_pkt.ethertype == 34525:
            return

        # dpid is same as switch id
        dpid = dpid_to_str(datapath.id)

        '''
            load balancer - check if the packet is routed to the server at 10.0.0.42
            implemented at IP Layer (Layer 3)
        '''
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if ip_pkt:
            src_ip = ip_pkt.src
            dst_ip = ip_pkt.dst

            if dst_ip == "10.0.0.42" and dpid == "0000000000000001":

                # install rules if routing for the first time
                if self.turn == -1:
                    self.logger.info("setting up round robin rules at switch 1")

                    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]

                    # h1
                    match = datapath.ofproto_parser.OFPMatch(eth_type=0x0800,ipv4_src=self.host_to_ip["h1"],ipv4_dst=dst_ip)
                    self.__add_flow(datapath, 2, match, actions=actions)
                    # h2
                    match = datapath.ofproto_parser.OFPMatch(eth_type=0x0800,ipv4_src=self.host_to_ip["h2"],ipv4_dst=dst_ip)
                    self.__add_flow(datapath, 2, match, actions=actions)
                    # h3
                    match = datapath.ofproto_parser.OFPMatch(eth_type=0x0800,ipv4_src=self.host_to_ip["h3"],ipv4_dst=dst_ip)
                    self.__add_flow(datapath, 2, match, actions=actions)

                    # start round robin
                    self.turn = 0

                # route to h4 or h5 depending on turn
                if self.turn == 0:
                    dst_mac = self.host_to_mac["h4"]
                    self.logger.info("routing 10.0.0.42 to h4 at mac address = {}".format(self.host_to_mac["h4"]))
                else:
                    dst_mac = self.host_to_mac["h5"]
                    self.logger.info("routing 10.0.0.42 to h5 at mac address = {}".format(self.host_to_mac["h5"]))

                # round robin turns
                self.turn = 1 - self.turn
        
        '''
            Learning Switch - 
            check if mac address to port mapping has been learned
            implemented at Ethernet Layer (Layer 2)
        '''

        src_mac = eth_pkt.src
        dst_mac = eth_pkt.dst

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

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=in_port, actions=actions, data=data)
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