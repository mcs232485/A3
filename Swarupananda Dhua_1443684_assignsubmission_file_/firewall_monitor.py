from operator import attrgetter
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from ryu.lib import hub

LEARNING = True

class FirewallMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FirewallMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.mac_to_port = {}
        self.monitor_thread = hub.spawn(self.monitor)
        self.h3_pkt_count = 0

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        ofproto = dp.ofproto
        p = dp.ofproto_parser

        self.add_flow(dp, 0, p.OFPMatch(), [p.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)])
        self.firewall(dp, p)

    def firewall(self, dp, p):
        self.add_flow(dp, 10, p.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.2', ipv4_dst='10.0.0.5'), [])
        self.add_flow(dp, 10, p.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.5', ipv4_dst='10.0.0.2'), [])
        self.add_flow(dp, 10, p.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.3', ipv4_dst='10.0.0.5'), [])
        self.add_flow(dp, 10, p.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.5', ipv4_dst='10.0.0.3'), [])
        self.add_flow(dp, 10, p.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.1', ipv4_dst='10.0.0.4'), [])
        self.add_flow(dp, 10, p.OFPMatch(eth_type=0x0800, ipv4_src='10.0.0.4', ipv4_dst='10.0.0.1'), [])

    def add_flow(self, dp, priority, match, actions):
        ofproto = dp.ofproto
        p = dp.ofproto_parser
        dp.send_msg(p.OFPFlowMod(datapath=dp, priority=priority, match=match, instructions=[p.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]))

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def state_change_handler(self, ev):
        dp = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if dp.id not in self.datapaths:
                self.datapaths[dp.id] = dp
        elif ev.state == DEAD_DISPATCHER:
            if dp.id in self.datapaths:
                del self.datapaths[dp.id]

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofproto = dp.ofproto
        p = dp.ofproto_parser
        self.mac_to_port.setdefault(dp.id, {})

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst, src = eth_pkt.dst, eth_pkt.src

        self.mac_to_port[dp.id][src] = msg.match['in_port']

        out_port = self.mac_to_port[dp.id][dst] if (LEARNING and( dst in self.mac_to_port[dp.id])) else ofproto.OFPP_FLOOD
        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(dp, 1, p.OFPMatch(in_port=msg.match['in_port'], eth_dst=dst), [p.OFPActionOutput(out_port)])
        dp.send_msg(p.OFPPacketOut(datapath=dp, buffer_id=ofproto.OFP_NO_BUFFER, in_port=msg.match['in_port'], actions=[p.OFPActionOutput(out_port)], data=msg.data))

    def monitor(self):
        while True:
            hub.sleep(5)
            if 1 in self.datapaths:
                dp = self.datapaths[1]
                dp.send_msg( dp.ofproto_parser.OFPPortStatsRequest(dp, 0, dp.ofproto.OFPP_ANY))

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stat_request_handler(self, ev):
        for stat in sorted(ev.msg.body, key=attrgetter('port_no')):
            if stat.port_no == 3:
                self.h3_pkt_count += stat.rx_packets
                self.logger.info('Total packets received so far from H3 on S1 is %d', self.h3_pkt_count)