"""
Firewall + Monitor
"""


from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types, ipv4
from ryu.ofproto.ofproto_v1_3_parser import OFPMatch

class FireWallMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FireWallMonitor, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.blocked_ip_pairs = [("10.0.0.1", "10.0.0.4"), ("10.0.0.4", "10.0.0.1"), ("10.0.0.2", "10.0.0.5"), ("10.0.0.5", "10.0.0.2"), ("10.0.0.3", "10.0.0.5"), ("10.0.0.5", "10.0.0.3")]
        self.monitored_mac = '00:00:00:00:00:03'
        self.counted_h3_to_s1 = 0

    def add_flow(self, datapath, in_port, dst, src, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        # if eth.ethertype == 0x0800:  # 0x0800 is the EtherType for IPv4
        #     self.logger.info("Received an IPv4 packet")
        # else:
        #     self.logger.info("Received a non-IPv4 packet")

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src
        if src == self.monitored_mac:
            self.counted_h3_to_s1 += 1
            print("Found packet coming from h3 to s1")
            print("Have encounterd ", self.counted_h3_to_s1, " number of packets in this path till now")
        src_ip = None
        dst_ip = None
        for p in pkt:
            if isinstance(p, ipv4.ipv4):
                src_ip = p.src
                dst_ip = p.dst
                self.logger.info(f"Source IP: {src_ip}, Destination IP: {dst_ip}")
                break 

        dpid = datapath.id
        if dpid > 2:
            print("DPID = ", dpid)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        
        if (src_ip, dst_ip) in self.blocked_ip_pairs:
            actions = [] # Dropping the packet by doing no action
            out =datapath.ofproto_parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
                actions=actions, data=None)
            datapath.send_msg(out)
            self.add_flow(datapath, msg.in_port, dst, src, actions) ## Learn the rule of doing Dropping for this pair
        else:
            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
            # install a flow to avoid packet_in next time
            if out_port != ofproto.OFPP_FLOOD:
                self.add_flow(datapath, msg.in_port, dst, src, actions)

            
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = datapath.ofproto_parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
                actions=actions, data=data)
            datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)
