


###########################################################
#######  Student Name Avishek Mukhopadhyay                #
#######  Entry Number 2021MCS2125                         #
#######  Assignment   3                                   #
###########################################################


from  ryu.base import   app_manager
from ryu.controller.handler import  MAIN_DISPATCHER
from ryu.controller import   ofp_event 
from ryu.controller.handler import  set_ev_cls
from ryu.ofproto   import ofproto_v1_3 , ether , inet   
from ryu.controller.handler  import CONFIG_DISPATCHER  
from ryu.lib.packet  	 import  packet , ethernet , ether_types , arp  , tcp , ipv4
from ryu.lib.packet.packet   import   Packet  
import  random



###################################################################
#######  Class Name  LoadBalancing                                #
#######  Purpose Implementation of load balancing functionality   #
###################################################################
    
class LoadBalancing(  app_manager.RyuApp ):

      OFP_VERSIONS  =   [  ofproto_v1_3.OFP_VERSION ]  
        

     
      def   __init__(  self , *firstlevelargs , **secondlevelargs ):
                  super( LoadBalancing     , self ).__init__(*firstlevelargs  , **secondlevelargs  )
                  self.mappingof_mac_and_port   =   {}  
                  # My virtual ip for load balancing
                  self.my_load_balancing_ip = "10.0.0.42" 

                  self.my_load_balancing_mac = "AB:AB:AB:AB:AB:BC"  

                                      
                  self.loadbalancingsystems=[] 
                  self.no_of_message_processed= 0
                  # My list of server nodes i.e. host4 and host5
                  self.loadbalancingsystems.append(  {  'layer3ad':"10.0.0.4" ,    'layer2ad' : "00:00:00:00:10:14" ,    "portno" :  "4" }  )

                  self.loadbalancingsystems.append( {    'layer3ad'  :  "10.0.0.5" ,   'layer2ad' :  "00:00:00:00:10:15"  ,   "portno":"4" }  )


      # This function composes ARP respose
      def     compose_address_resolution_answer(self  ,    ip_address_target  , mac_destination  )  :               

                  new_arp_response = packet.Packet()

                  layer2_frame   =    ethernet.ethernet(  mac_destination   ,       self.my_load_balancing_mac  ,   2054  )   
                  response_inner_part   =  arp.arp(  1  ,   2048  ,    6   ,    4  ,  2  ,    self.my_load_balancing_mac  ,     self.my_load_balancing_ip   , mac_destination  , ip_address_target  )    

                  new_arp_response.add_protocol(  layer2_frame  )  
                  new_arp_response.add_protocol(  response_inner_part )
                  new_arp_response.serialize( )

                  return new_arp_response

      # data transfer or flow creation function
      def     introduce_data_transfer(self, routevar, precedence, similarity, jobs, buffer_id=None):

                  anothervar = [  routevar.ofproto_parser.OFPInstructionActions(  routevar.ofproto.OFPIT_APPLY_ACTIONS ,  jobs )  ]   

                  if   buffer_id   ==   None:
                       changedvalue   =  routevar.ofproto_parser.OFPFlowMod(    datapath =  routevar ,  priority =precedence,match = similarity, instructions = anothervar   )   

                  else:
                       changedvalue  =   routevar.ofproto_parser.OFPFlowMod(  datapath = routevar, buffer_id  = buffer_id , priority=precedence  , match=similarity , instructions = anothervar )  

                  routevar.send_msg(  changedvalue  )
        
      # This function configures the initial nature of the learning switch
      @set_ev_cls(  ofp_event.EventOFPSwitchFeatures  ,   CONFIG_DISPATCHER  )  
      def    handiling_switch_functionality(   self  ,   myvar  )  :
                  self.introduce_data_transfer(  myvar.msg.datapath  ,   0  ,   myvar.msg.datapath.ofproto_parser.OFPMatch()  ,   [  myvar.msg.datapath.ofproto_parser.OFPActionOutput(   myvar.msg.datapath.ofproto.OFPP_CONTROLLER ,   myvar.msg.datapath.ofproto.OFPCML_NO_BUFFER )  ]  ) 



      # This function is called when ever a data packet is received
      @set_ev_cls(    ofp_event.EventOFPPacketIn  ,   MAIN_DISPATCHER  )                  
      def      per_packet_handling_function(  self ,   myvar ) :
 
               new_created_packet   =    packet.Packet(  myvar.msg.data )
   
               new_created_frame     =    new_created_packet.get_protocols( ethernet.ethernet  )[ 0 ]  
               # Ignore link layer discovery packets
               if   new_created_frame.ethertype  == ether_types.ETH_TYPE_LLDP  :  
                         return
               # If ARP packet is received
               if  new_created_frame.ethertype   ==   ether.ETH_TYPE_ARP :                                              

                      if    new_created_packet.get_protocols( arp.arp  )[ 0  ].dst_ip   == self.my_load_balancing_ip   and new_created_packet.get_protocols(  arp.arp  )[ 0 ].opcode  == arp.ARP_REQUEST  :                
                            data_packet_to_respond  =  self.compose_address_resolution_answer(  new_created_packet.get_protocols( arp.arp  )[  0 ].src_ip  ,   new_created_packet.get_protocols(  arp.arp )[  0 ].src_mac )    
                            # Send modified arp response
                            myvar.msg.datapath.send_msg(  myvar.msg.datapath.ofproto_parser.OFPPacketOut(   datapath =  myvar.msg.datapath  ,  in_port =  myvar.msg.datapath.ofproto.OFPP_ANY  , data  =  data_packet_to_respond.data  ,   actions =  [ myvar.msg.datapath.ofproto_parser.OFPActionOutput(   myvar.msg.match[ 'in_port'  ] ) ]  , buffer_id=0xffffffff )  )

                      else:                                                                                
                           self.mappingof_mac_and_port.setdefault(  myvar.msg.datapath.id ,  { }  ) 

                           self.mappingof_mac_and_port[  myvar.msg.datapath.id   ][  new_created_frame.src  ] = myvar.msg.match[  'in_port'  ]  

                           if     new_created_frame.dst   in   self.mac_to_port[  myvar.msg.datapath.id ]  :  
                                  final_target   =  self.mappingof_mac_and_port[  myvar.msg.datapath.id  ][  new_created_frame.dst ]

                           else:
                                  final_target    =   myvar.msg.datapath.ofproto.OFPP_FLOOD

                           if   final_target   !=   myvar.msg.datapath.ofproto.OFPP_FLOOD  :
                                if myvar.msg.buffer_id != myvar.msg.datapath.ofproto.OFP_NO_BUFFER:
                                   self.introduce_data_transfer(myvar.msg.datapath, 1, myvar.msg.datapath.ofproto_parser.OFPMatch(  in_port  = myvar.msg.match[ 'in_port' ] , eth_dst  = new_created_frame.dst )  , [myvar.msg.datapath.ofproto_parser.OFPActionOutput(final_target)], myvar.msg.buffer_id)
                                   return
                                else:  
                                   self.introduce_data_transfer(myvar.msg.datapath, 1, myvar.msg.datapath.ofproto_parser.OFPMatch(  in_port  = myvar.msg.match[ 'in_port' ] , eth_dst  = new_created_frame.dst )  , [myvar.msg.datapath.ofproto_parser.OFPActionOutput(final_target)])
                           innercontent = None
                           if   myvar.msg.buffer_id   ==  myvar.msg.datapath.ofproto.OFP_NO_BUFFER :
                                    innercontent  =    msg.data  
                           myvar.msg.datapath.send_msg( myvar.msg.datapath.ofproto_parser.OFPPacketOut( datapath = myvar.msg.datapath  ,   buffer_id =  myvar.msg.buffer_id ,  in_port  =  myvar.msg.match[ 'in_port' ]  ,    actions   =   [   myvar.msg.datapath.ofproto_parser.OFPActionOutput(  final_target ) ] ,    data  = innercontent )  ) 
                      return
               if   new_created_packet.get_protocols(  ipv4.ipv4  )  == [] : 
                     return
               # Send select target host in round robin fashion 
               target_outport_to_be_sentstr   =    self.loadbalancingsystems[  self.no_of_message_processed   %  2   ][ 'portno' ]
               target_outport_to_be_sent   =  int( target_outport_to_be_sentstr  )  
               target_ip_to_be_sent   =   self.loadbalancingsystems[  self.no_of_message_processed   %    2  ][  'layer3ad'  ]  
               target_mac_to_be_sent    =   self.loadbalancingsystems[  self.no_of_message_processed   %  2   ][  'layer2ad'   ]  
               str_print  =  "Selected Target Server ip is "   +   self.loadbalancingsystems[  self.no_of_message_processed  %   2  ][  'layer3ad'  ]
               # Track number of packet processed  
               self.no_of_message_processed   =   self.no_of_message_processed  +   1  
               #   Process request towards server
               myvar.msg.datapath.send_msg(  myvar.msg.datapath.ofproto_parser.OFPFlowMod(  datapath =    myvar.msg.datapath ,  match =  myvar.msg.datapath.ofproto_parser.OFPMatch(  in_port =  myvar.msg.match['in_port'] ,   eth_type  =  new_created_frame.ethertype  ,   eth_src =  new_created_frame.src  , eth_dst =  new_created_frame.dst  ,  ip_proto =    new_created_packet.get_protocols( ipv4.ipv4  )[ 0  ].proto   ,  ipv4_src  =  new_created_packet.get_protocols( ipv4.ipv4 )[ 0  ].src  ,   ipv4_dst =   new_created_packet.get_protocols( ipv4.ipv4 )[  0 ].dst )  ,   idle_timeout  = 7  ,  instructions = [  myvar.msg.datapath.ofproto_parser.OFPInstructionActions(  myvar.msg.datapath.ofproto.OFPIT_APPLY_ACTIONS   ,  [ myvar.msg.datapath.ofproto_parser.OFPActionSetField(  ipv4_src  = self.my_load_balancing_ip   )  , myvar.msg.datapath.ofproto_parser.OFPActionSetField( eth_src  =  self.my_load_balancing_mac  ) ,   myvar.msg.datapath.ofproto_parser.OFPActionSetField( eth_dst  = target_mac_to_be_sent  ) ,   myvar.msg.datapath.ofproto_parser.OFPActionSetField(  ipv4_dst  = target_ip_to_be_sent  )   ,  myvar.msg.datapath.ofproto_parser.OFPActionOutput(  target_outport_to_be_sent   )  ]  ) ] ,  buffer_id    =  myvar.msg.buffer_id ,   cookie = random.randint( 0  ,  0xffffffffffffffff ) ) ) 
               print( "\n \n \n  Data Packet from ip: " + str(  new_created_packet.get_protocols( ipv4.ipv4 )[  0 ].src )  )  
               print(  "Data Packet dest ip :  "  + self.my_load_balancing_ip  )       
               print( str_print    )
               print(  "Data Packet sent to  :  "   + str(  target_ip_to_be_sent )  ) 
               #   Process response from server 
               myvar.msg.datapath.send_msg(  myvar.msg.datapath.ofproto_parser.OFPFlowMod(   datapath =  myvar.msg.datapath   ,  match =  myvar.msg.datapath.ofproto_parser.OFPMatch(  in_port =  target_outport_to_be_sent ,  eth_type =  new_created_frame.ethertype  ,   eth_src  =   target_mac_to_be_sent ,  eth_dst =  self.my_load_balancing_mac ,  ip_proto  = new_created_packet.get_protocols(  ipv4.ipv4 )[ 0  ].proto   ,   ipv4_src = target_ip_to_be_sent ,   ipv4_dst =  self.my_load_balancing_ip  ) ,  idle_timeout = 7 ,   instructions  = [  myvar.msg.datapath.ofproto_parser.OFPInstructionActions(  myvar.msg.datapath.ofproto.OFPIT_APPLY_ACTIONS  ,  [ myvar.msg.datapath.ofproto_parser.OFPActionSetField(  eth_src = self.my_load_balancing_mac  ) ,   myvar.msg.datapath.ofproto_parser.OFPActionSetField(  ipv4_src = self.my_load_balancing_ip ) ,  myvar.msg.datapath.ofproto_parser.OFPActionSetField(  ipv4_dst  = new_created_packet.get_protocols(  ipv4.ipv4  )[ 0 ].src  )  , myvar.msg.datapath.ofproto_parser.OFPActionSetField(  eth_dst =  new_created_frame.src ) ,   myvar.msg.datapath.ofproto_parser.OFPActionOutput(  myvar.msg.match[ 'in_port'  ] )   ]  )  ] ,   cookie =  random.randint(  0,   0xffffffffffffffff  ) )  ) 
               print( "  \n \n \n  Sending Reply from: "   + str(  target_ip_to_be_sent )  ) 
               print(  " Sending reply to  "  + str(  new_created_packet.get_protocols(   ipv4.ipv4 )[ 0  ].src )  )  
