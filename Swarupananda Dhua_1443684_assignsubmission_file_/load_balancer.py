from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_int
from ryu.lib.packet.ether_types import ETH_TYPE_ARP, ETH_TYPE_IP, ETH_TYPE_LLDP
from ryu.lib.packet import arp, ethernet, ipv4, packet

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        ofproto = dp.ofproto
        p = dp.ofproto_parser
        self.add_flow(dp, 0, p.OFPMatch(), [p.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)])

    def add_flow(self, dp, priority, match, actions, buffer_id=None):
        ofproto = dp.ofproto
        p = dp.ofproto_parser

        inst = [p.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = p.OFPFlowMod(datapath=dp, buffer_id=buffer_id, priority=priority, match=match, instructions=inst)
        else:
            mod = p.OFPFlowMod(datapath=dp, priority=priority, match=match, instructions=inst)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofproto = dp.ofproto
        p = dp.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ETH_TYPE_LLDP:
            return

        dst_mac, src_mac = eth.dst, eth.src

        self.mac_to_port.setdefault(dp.id, {})
        self.mac_to_port[dp.id][src_mac] = in_port

        out_port = self.mac_to_port[dp.id][dst_mac] if (dst_mac in self.mac_to_port[dp.id]) else ofproto.OFPP_FLOOD

        if out_port != ofproto.OFPP_FLOOD:
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(dp, 1, p.OFPMatch(in_port=in_port, eth_dst=dst_mac, eth_src=src_mac), [p.OFPActionOutput(out_port)], msg.buffer_id)
                return
            else:
                self.add_flow(dp, 1, p.OFPMatch(in_port=in_port, eth_dst=dst_mac, eth_src=src_mac), [p.OFPActionOutput(out_port)])

        if dp.id == 1:
            if eth.ethertype == ETH_TYPE_ARP:
                arp_header = pkt.get_protocol(arp.arp)

                if arp_header.dst_ip == '10.0.0.42' and arp_header.opcode == arp.ARP_REQUEST:
                    arppkt = packet.Packet()
                    src_mac = '00:00:00:00:00:04' if (haddr_to_int(arp_header.src_mac) % 2 == 1) else '00:00:00:00:00:05'
                    arppkt.add_protocol(ethernet.ethernet(dst=arp_header.src_mac, src=src_mac, ethertype=ETH_TYPE_ARP))
                    arppkt.add_protocol(arp.arp(opcode=arp.ARP_REPLY, src_mac=src_mac, src_ip='10.0.0.42', dst_mac=arp_header.src_mac, dst_ip=arp_header.src_ip))
                    arppkt.serialize()
                    dp.send_msg(p.OFPPacketOut(datapath=dp, in_port=ofproto.OFPP_ANY, data=arppkt.data, actions=[p.OFPActionOutput(in_port)], buffer_id=0xffffffff))
                    return
            if eth.ethertype == ETH_TYPE_IP:
                ip_header = pkt.get_protocol(ipv4.ipv4)
                if ip_header.dst == '10.0.0.42':
                    server_dst_ip = '10.0.0.4' if (dst_mac == '00:00:00:00:00:04') else '10.0.0.5'
                    self.add_flow(dp, 2, p.OFPMatch(in_port=in_port, eth_type=ETH_TYPE_IP, ip_proto=ip_header.proto, ipv4_dst='10.0.0.42'), [p.OFPActionSetField(ipv4_dst=server_dst_ip), p.OFPActionOutput(4)])
                    self.add_flow(dp, 2, p.OFPMatch(in_port=4, eth_type=ETH_TYPE_IP, ip_proto=ip_header.proto, ipv4_src=server_dst_ip, eth_dst=src_mac), [p.OFPActionSetField(ipv4_src='10.0.0.42'), p.OFPActionOutput(in_port)])
                    return

            data = msg.data if (msg.buffer_id == ofproto.OFP_NO_BUFFER) else None
            dp.send_msg(p.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=in_port, actions=[p.OFPActionSetField(ipv4_src='10.0.0.42'), p.OFPActionOutput(in_port)], data=data))
        else:
            dp.send_msg(p.OFPPacketOut(datapath=dp, buffer_id=ofproto.OFP_NO_BUFFER, in_port=in_port, actions=[p.OFPActionOutput(out_port)], data=msg.data))