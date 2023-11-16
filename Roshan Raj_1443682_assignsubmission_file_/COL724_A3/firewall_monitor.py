from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto.ofproto_v1_3_parser import OFPMatch
from ryu.ofproto.ofproto_v1_3_parser import OFPActionOutput
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet, ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp

class FirewallMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FirewallMonitor, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.blocked_hosts = {'H2', 'H3', 'H4'}
        self.monitor_host = 'H3'
        self.packet_count = 0

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install a table-miss flow entry to send all unmatched traffic to the controller
        match = OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        ip4_pkt = pkt.get_protocol(ipv4.ipv4)
        tcp_pkt = pkt.get_protocol(tcp.tcp)

        if ip4_pkt is None or tcp_pkt is None:
            # Ignore non-IPv4 or non-TCP packets
            return

        eth_src = eth.src
        eth_dst = eth.dst
        src_ip = ip4_pkt.src
        dst_ip = ip4_pkt.dst

        self.mac_to_port.setdefault(datapath.id, {})

        # Block specific host communication
        if eth_src in self.blocked_hosts or eth_dst in self.blocked_hosts:
            self.logger.info("Blocked: %s to %s (in_port %d)",
                             eth_src, eth_dst, in_port)
            return

        self.logger.info("Allowed: %s to %s (in_port %d)", eth_src, eth_dst, in_port)

        if eth_src not in self.mac_to_port[datapath.id]:
            self.mac_to_port[datapath.id][eth_src] = in_port

        out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

        # Monitor packet count from a specific host
        if eth_src == self.monitor_host:
            self.packet_count += 1
            self.logger.info("Packet count from %s: %d", self.monitor_host, self.packet_count)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

if __name__ == '__main__':
    from ryu.cmd import manager
    manager.main()
