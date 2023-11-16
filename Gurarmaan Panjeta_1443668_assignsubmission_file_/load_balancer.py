'''
Round Robin Load Balancer
'''

import random
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types, arp, tcp, ipv4, icmp
from ryu.ofproto import ether, inet
from ryu.ofproto import ofproto_v1_3

    
class LoadBalancer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(LoadBalancer, self).__init__(*args, **kwargs)
        self.serverIPs = ["10.0.0.4", "10.0.0.5"]        
        self.serverMACs = ["00:00:00:00:00:04", "00:00:00:00:00:05"]     
        self.serverPorts = [1, 1]                    # S2's port ID 1 is connected to S1 
        self.virtual_ip = "10.0.0.42"                # Load Balancer's IP
        self.virtual_mac = "88:88:88:88:88:88"       # Load Balancer's MAC Address
        self.last_alloted_to_h4 = False                 # To figure out turn in Round Robin
        
        print("Done with initial setup related to server list creation.")
        

    ## Initial Configuration that allows all unmatched entries to go to the controller
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        #print("Adding flow for flow w priority: ", priority )
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            #print("here")
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        #print("here 1!")
        datapath.send_msg(mod)
        #print("here 2!")
        return

    def function_for_arp_reply(self, dst_ip, dst_mac): # Craft an ARP Reply packet with appropriate headers
        print("{ Creating ARP reply with correct src_mac for server : ")
        arp_target_mac = dst_mac
        src_ip = self.virtual_ip                   
        src_mac = self.virtual_mac

        pkt = packet.Packet() ## Creating an Empty Packet
        ether_frame = ethernet.ethernet(dst_mac, src_mac, 2054)   ## Ethernet header data  
        arp_reply_pkt = arp.arp(1, 2048, 6, 4, 2, src_mac, src_ip, arp_target_mac, dst_ip)   # ARP header data
        pkt.add_protocol(ether_frame)
        pkt.add_protocol(arp_reply_pkt)
        pkt.serialize() ## Compiling everything
        print(": ARP Reply Packet created }")
        return pkt
    

    ## In Case an error comes up, prints it
    @set_ev_cls(ofp_event.EventOFPErrorMsg, MAIN_DISPATCHER)
    def error_msg_handler(self, ev):
        error_msg = ev.msg
        print("ERROR : ", error_msg)
        return
    

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)                
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        #print("IN PORT = ", in_port)
        dpid = datapath.id
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP: # ignoring lldp packet
            return
        
        if dpid == 2: ## Switch 2, basic and static rules
            match1 = parser.OFPMatch(eth_dst="00:00:00:00:00:04") ## If going to h4, output to port 2
            actions1 = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, 4, match1, actions1)

            match2 = parser.OFPMatch(eth_dst="00:00:00:00:00:05") ## If going to h5, output to port 3
            actions2 = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 4, match2, actions2)

            match3 = parser.OFPMatch() ## For all others, throw at S1 via port 1
            actions3 = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 2, match3, actions3)
            return

        ## Switch 1
        if eth.ethertype == ether.ETH_TYPE_ARP:      
            arp_header = pkt.get_protocols(arp.arp)[0]
            
            ## Checks whether ARP Request for the virtual IP of the Server, if yes, sends the ARP Reply with the virtal mac
            if arp_header.dst_ip == self.virtual_ip and arp_header.opcode == arp.ARP_REQUEST:              

                reply_packet=self.function_for_arp_reply(arp_header.src_ip, arp_header.src_mac) ## Dest IP, Dest MAC  
                actions = [parser.OFPActionOutput(in_port)]
                packet_out = parser.OFPPacketOut(datapath=datapath, in_port=ofproto.OFPP_ANY, data=reply_packet.data, actions=actions, buffer_id=0xffffffff)    
                datapath.send_msg(packet_out)
                print("Sending Reply packet to in_port = ", in_port)
                #return


                if self.last_alloted_to_h4:
                    #Round robin fashion setup
                    server_ip_allot = self.serverIPs[1]
                    server_mac_allot = self.serverMACs[1]
                    server_port_allot = self.serverPorts[1]
                    print("The server alloted to this host is ip, mac, port ===> ", server_ip_allot, server_mac_allot, server_port_allot)
                    self.last_alloted_to_h4 = False
                else:
                    server_ip_allot = self.serverIPs[0]
                    server_mac_allot = self.serverMACs[0]
                    server_port_allot = self.serverPorts[0]
                    print("The server alloted to this host is ip, mac, port ===> ", server_ip_allot, server_mac_allot, server_port_allot)
                    self.last_alloted_to_h4 = True

                print("Installing Route to server!")
                
                #Installing Route from node to server in S1
                match = parser.OFPMatch(in_port=in_port, ## For all messages on this port
                                        eth_src=eth.src, ## and (src, dst) pair, forward to the allotted server
                                        eth_dst=eth.dst,  
                                        #ipv4_src=iphdr.src,
                                        #ipv4_dst=self.virtual_ip
                                        )

                actions = [ parser.OFPActionSetField(eth_dst=server_mac_allot), # Set Destination to allocated server
                            parser.OFPActionOutput(server_port_allot) ## Send to S2 via port 1
                            #parser.OFPActionSetField(ipv4_dst=server_ip_allot), 
                            ] 
                
                self.add_flow(datapath, 2, match, actions)
                print("Packet from : " + str(arp_header.src_ip) + ",  sent to Server at : "+str(server_ip_allot)+", with MAC: "+str(server_mac_allot)+" and on switch port: "+str(server_port_allot))  


                print("Reverse route from server!")
                #Reverse route from server to node in S1
                match2 = parser.OFPMatch(in_port=server_port_allot, # Message Comes from this port
                                        eth_src=server_mac_allot,   # Arriving from h4 or h5's MAC
                                        eth_dst=eth.src,            # With destination to requesting host
                                        #ipv4_src=server_ip_allot, 
                                        #ipv4_dst=iphdr.src
                                        )
                actions2 = [ parser.OFPActionSetField(eth_src=self.virtual_mac), # Modify so that it looks like the packet comes from Server's MAC
                            parser.OFPActionSetField(eth_dst=eth.src),           # Set Destination to requesting host
                            parser.OFPActionOutput(in_port)                      ## Send to host via port in_port
                            #parser.OFPActionSetField(ipv4_src=self.virtual_ip),  
                            #parser.OFPActionSetField(ipv4_dst=iphdr.src),
                            ]
                self.add_flow(datapath, 1, match2, actions2)
                print("Reply sent from server: " + str(server_ip_allot)+", with MAC: "+str(server_mac_allot)+" via load balancer : "+str(self.virtual_ip)+" to : "+str(arp_header.src_ip))