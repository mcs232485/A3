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
        self.mac_to_port = {}
        self.rules = {}
        self.count = -1
        self.host_to_mac = {
            "h1" : "00:00:00:00:00:01",
            "h2" : "00:00:00:00:00:02",
            "h3" : "00:00:00:00:00:03",
            "h4" : "00:00:00:00:00:04",
            "h5" : "00:00:00:00:00:05"
        }
        self.host_to_ip = {
            "h1" : "10.0.0.1",
            "h2" : "10.0.0.2",
            "h3" : "10.0.0.3",
            "h4" : "10.0.0.4",
            "h5" : "10.0.0.5",
        }
        self.mac_to_ip = {
            "00:00:00:00:00:01" : "10.0.0.1", "00:00:00:00:00:02" : "10.0.0.2", "00:00:00:00:00:03" : "10.0.0.3", "00:00:00:00:00:04" : "10.0.0.42", "00:00:00:00:00:05" : "10.0.0.42",
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
        self.add_flow(datapath, 0, match, actions)

    def debugger_print(self,a):
        print("Debugging at: ", a)
        return a+1

    def add_flow(self, datapath, priority, match, actions):
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

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        debug_num =0
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        new_rules = False
        datapath = msg.datapath
        ofproto = msg.datapath.ofproto
        parser = msg.datapath.ofproto_parser
        in_port = msg.match['in_port']
        flag = True
        dpid = msg.datapath.id
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ip_packet = False
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None

        
        if not eth:
            flag = False
            return

        # if eth.ethertype == ether_types.ETH_TYPE_LLDP:
        #     # ignore lldp packet
        #     flag = False
        #     return

        # ignore default packets
        elif eth.ethertype == 34525:
            flag = False
            return

        # dpid is same as switch id
        dpid = dpid_to_str(datapath.id)

        '''
            load balancer - check if the packet is routed to the server at 10.0.0.42
            implemented at IP Layer (Layer 3)
        '''
        ip_header = pkt.get_protocol(ipv4.ipv4)
        if flag and ip_header:
            src_ip = ip_header.src
            dst_ip = ip_header.dst

            if ip_packet:
                print("hi")
                src_ip = ip_packet.src
                dst_ip = ip_packet.dst

                if src_ip in ['10.0.0.1', '10.0.0.2', '10.0.0.3'] and dst_ip == '10.0.0.42':
                    # Implement load balancing based on round-robin count

                    count = self.count % 2  # Two servers (h4 and h5)
                    server_ips = ['10.0.0.42', '10.0.0.42']
                    out_port = self.mac_to_port[dpid][server_ips[count]]
                    self.count += 1
                    actions = [parser.OFPActionOutput(out_port)]
                    data = msg.data
                    out = parser.OFPPacketOut(
                        datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                        in_port=msg.in_port, actions=actions, data=data)
                    datapath.send_msg(out)
                    
                    # Print which server is serving and which host IP sent the message
                    serving_server = server_ips[count]
                    print(f"Server {serving_server} serving request from {src_ip}")
                    return

            

            if flag and dst_ip == "10.0.0.42" and dpid == "0000000000000001":

                # install rules if routing for the first time
                if self.count == -1:
                    # debug_num = 5
                    # for i in range(temp_num):
                    new_rules = True
                    debug_num = 152
                    self.debugger_print(debug_num)
                    actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
                    match = datapath.ofproto_parser.OFPMatch(eth_type=0x0800,ipv4_src=self.mac_to_ip[self.host_to_mac["h1"]],ipv4_dst=dst_ip)
                    self.add_flow(datapath, 2, match, actions=actions)
                    self.debugger_print(debug_num)
                    match = datapath.ofproto_parser.OFPMatch(eth_type=0x0800,ipv4_src=self.mac_to_ip[self.host_to_mac["h1"]],ipv4_dst=dst_ip)
                    self.add_flow(datapath, 2, match, actions=actions)
                    match = datapath.ofproto_parser.OFPMatch(eth_type=0x0800,ipv4_src=self.mac_to_ip[self.host_to_mac["h1"]],ipv4_dst=dst_ip)
                    self.add_flow(datapath, 2, match, actions=actions)
                    self.debugger_print(debug_num)
                    self.count = 0
                    print("count info:,", self.count)

                # route to h4 or h5 depending on count
                if self.count == 0:
                    self.debugger_print(debug_num)
                    dst_mac = self.host_to_mac["h4"]
                    print("routing 10.0.0.42 at h4 at corresponding MAC :", self.host_to_mac["h4"])
                else:
                    dst_mac = self.host_to_mac["h5"]
                    self.debugger_print(debug_num)
                    print("routing 10.0.0.42 at h5 at corresponding MAC :", self.host_to_mac["h5"])

                # round robin counts
                self.count +=1
                self.count = self.count % 2

        src_mac = eth.src
        dst_mac = eth.dst
        self.debugger_print(debug_num)

        if dpid_to_str(datapath.id) not in self.rules:
            self.rules[dpid_to_str(datapath.id)] = {}

        if ip_packet:
            print("hi")
            src_ip = ip_packet.src
            dst_ip = ip_packet.dst

            if src_ip in ['10.0.0.1', '10.0.0.2', '10.0.0.3'] and dst_ip == '10.0.0.42':
                # Implement load balancing based on round-robin count

                count = self.count % 2  # Two servers (h4 and h5)
                server_ips = ['10.0.0.42', '10.0.0.42']
                out_port = self.mac_to_port[dpid][server_ips[count]]
                self.count += 1
                actions = [parser.OFPActionOutput(out_port)]
                data = msg.data
                out = parser.OFPPacketOut(
                    datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                    in_port=msg.in_port, actions=actions, data=data)
                datapath.send_msg(out)
                
                # Print which server is serving and which host IP sent the message
                serving_server = server_ips[count]
                print(f"Current Server is{serving_server} and ip is{src_ip}")
                return

        if src_mac not in self.rules[dpid_to_str(datapath.id)]:
            self.logger.info("New Mac {}  port number is {}".format(src_mac,in_port))
            self.debugger_print(debug_num)
            self.rules[dpid_to_str(datapath.id)][eth.src] = in_port
        out_port = ofproto.OFPP_FLOOD
        if ip_packet:
            print("hi")
            src_ip = ip_packet.src
            dst_ip = ip_packet.dst

            if src_ip in ['10.0.0.1', '10.0.0.2', '10.0.0.3'] and dst_ip == '10.0.0.42':
                # Implement load balancing based on round-robin count

                count = self.count % 2  # Two servers (h4 and h5)
                server_ips = ['10.0.0.42', '10.0.0.42']
                out_port = self.mac_to_port[dpid][server_ips[count]]
                self.count += 1
                actions = [parser.OFPActionOutput(out_port)]
                data = msg.data
                out = parser.OFPPacketOut(
                    datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                    in_port=msg.in_port, actions=actions, data=data)
                datapath.send_msg(out)
                
                # Print which server is serving and which host IP sent the message
                serving_server = server_ips[count]
                print(f"Current Server is{serving_server} and ip is{src_ip}")
                return
        if dst_mac in self.rules[dpid_to_str(datapath.id)]:
            out_port = self.rules[dpid_to_str(datapath.id)][dst_mac]
        actions = [parser.OFPActionOutput(out_port)]
        debug_num = 242
        self.debugger_print(debug_num)
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
            self.add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
        return

    