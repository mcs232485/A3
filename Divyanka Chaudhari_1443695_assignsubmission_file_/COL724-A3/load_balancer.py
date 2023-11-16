from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, ipv4
from ryu.lib import mac, ip


class LoadBalancer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(LoadBalancer, self).__init__(*args, **kwargs)
        # Virtual IP and MAC address for the load balancer
        self.virtual_ip = "10.0.0.42"
        self.virtual_mac = "AA:BB:CC:DD:EE:FF"
        # Real servers' IP and MAC addresses
        self.servers = [
            {'ip': '10.0.0.4', 'mac': '00:00:00:00:00:04', 'port': 1},
            {'ip': '10.0.0.5', 'mac': '00:00:00:00:00:05', 'port': 2}
        ]
        self.server_index = 0

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        # Handle ARP requests for the virtual IP
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            arp_pkt = pkt.get_protocol(arp.arp)
            if arp_pkt.opcode == arp.ARP_REQUEST and arp_pkt.dst_ip == self.virtual_ip:
                self.reply_arp(datapath, arp_pkt, eth, msg.in_port)
                return

        # Handle IPv4 packets
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            if ip_pkt.dst == self.virtual_ip:
                self.round_robin_load_balance(
                    datapath, ip_pkt, eth, msg.in_port)
                return

    def reply_arp(self, datapath, arp_pkt, eth, port):
        # Generate an ARP reply with the virtual MAC address
        arp_reply = packet.Packet()
        arp_reply.add_protocol(ethernet.ethernet(
            ethertype=eth.ethertype,
            dst=eth.src,
            src=self.virtual_mac))
        arp_reply.add_protocol(arp.arp(
            opcode=arp.ARP_REPLY,
            src_mac=self.virtual_mac,
            src_ip=self.virtual_ip,
            dst_mac=arp_pkt.src_mac,
            dst_ip=arp_pkt.src_ip))
        arp_reply.serialize()

        actions = [datapath.ofproto_parser.OFPActionOutput(port)]
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=datapath.ofproto.OFP_NO_BUFFER,
            in_port=datapath.ofproto.OFPP_CONTROLLER,
            actions=actions,
            data=arp_reply.data)
        datapath.send_msg(out)

    def round_robin_load_balance(self, datapath, ip_pkt, eth, port):
        # Round-robin server selection
        server = self.servers[self.server_index]
        self.server_index = (self.server_index + 1) % len(self.servers)

        # Setup flow to server
        actions = [
            datapath.ofproto_parser.OFPActionSetField(ipv4_dst=server['ip']),
            datapath.ofproto_parser.OFPActionSetField(eth_dst=server['mac']),
            datapath.ofproto_parser.OFPActionOutput(server['port'])
        ]
        match = parser.OFPMatch(
            in_port=port,
            eth_type=ether_types.ETH_TYPE_IP,
            eth_src=eth.src,
            eth_dst=eth.dst,
            ipv4_dst=ip_pkt.dst
        )
        self.add_flow(datapath, 1, match, actions)

    def add_flow(self, datapath, priority, match, actions, timeout=10):
        # Add a flow with a hard timeout to the switch
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match,
            instructions=inst, hard_timeout=timeout)
        datapath.send_msg(mod)
