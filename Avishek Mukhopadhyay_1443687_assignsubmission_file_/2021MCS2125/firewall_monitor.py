
###########################################################
#######  Student Name Avishek Mukhopadhyay                #
#######  Entry Number 2021MCS2125                         #
#######  Assignment   3                                   #
###########################################################


from  ryu.base import   app_manager
from ryu.controller.handler import  MAIN_DISPATCHER
from ryu.controller import   ofp_event 
from ryu.controller.handler import  set_ev_cls
from ryu.ofproto   import ofproto_v1_3  
from ryu.controller.handler  import CONFIG_DISPATCHER  
from ryu.lib.packet  	 import packet, ethernet, ether_types 



###################################################################
#######  Class Name  FirewallSwitch                               #
#######  Purpose Implementation of firewall switch functionality  #
###################################################################
class FirewallSwitch(  app_manager.RyuApp ):
      #Open Flow Version to be mentioned
      OFP_VERSIONS  =   [  ofproto_v1_3.OFP_VERSION ]  
        

     
      def   __init__(  self , *firstlevelargs , **secondlevelargs ):
            super( FirewallSwitch     , self ).__init__(*firstlevelargs  , **secondlevelargs  )
            self.mappingof_mac_and_port   =   {}    


      # data transfer or flow creation function
      def     introduce_data_transfer(self, routevar, precedence, similarity, jobs, buffer_id=None):

            anothervar = [  routevar.ofproto_parser.OFPInstructionActions(  routevar.ofproto.OFPIT_APPLY_ACTIONS ,  jobs )  ]   

            if   buffer_id   ==   None:
                 changedvalue   =  routevar.ofproto_parser.OFPFlowMod(    datapath =  routevar ,  priority =precedence,match = similarity, instructions = anothervar   )   

            else:
                 changedvalue  =   routevar.ofproto_parser.OFPFlowMod(  datapath = routevar, buffer_id  = buffer_id , priority=precedence  , match=similarity , instructions = anothervar )  

            routevar.send_msg(  changedvalue  )


      # This function configures the initial nature of the firewall switch
      @set_ev_cls(  ofp_event.EventOFPSwitchFeatures , CONFIG_DISPATCHER  )
      def   function_for_switch(  self , myvar ):  
            self.introduce_data_transfer( myvar.msg.datapath  , 0  , myvar.msg.datapath.ofproto_parser.OFPMatch() , [ myvar.msg.datapath.ofproto_parser.OFPActionOutput(  myvar.msg.datapath.ofproto.OFPP_CONTROLLER  , myvar.msg.datapath.ofproto.OFPCML_NO_BUFFER ) ]  )   




      # This function is called when ever a data packet is received
      @set_ev_cls(    ofp_event.EventOFPPacketIn  , MAIN_DISPATCHER  )   
      def   function_for_packet(  self   , myvar  ):  
            tmpval = None
            # Ignore link layer discovery packets
            if   packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].ethertype   ==  ether_types.ETH_TYPE_LLDP:
                 return
            self.mappingof_mac_and_port.setdefault(  format( myvar.msg.datapath.id, "d" ).zfill( 16 ), {}  ) 
            # Rule for firewall packets
            if (packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src == "00:00:00:00:10:12" and packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].dst == "00:00:00:00:10:15") or (packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src == "00:00:00:00:10:15" and packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].dst == "00:00:00:00:10:12")  :
               return 
            # Rule for firewall packets
            if (packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src == "00:00:00:00:10:13" and packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].dst == "00:00:00:00:10:15") or (packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src == "00:00:00:00:10:15" and packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].dst == "00:00:00:00:10:13")  :
               return
            # Rule for firewall packets
            if (packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src == "00:00:00:00:10:11" and packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].dst == "00:00:00:00:10:14") or (packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src == "00:00:00:00:10:14" and packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].dst == "00:00:00:00:10:11")  :
               return

            if packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src == "00:00:00:00:10:13"  :
                 self.logger.info("Monitor H3 Generated Captured Packet with   %s   %s  %s  %s   "  ,  format(  myvar.msg.datapath.id , "d" ).zfill( 16  ) , packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src ,  packet.Packet(  myvar.msg.data ).get_protocols(  ethernet.ethernet )[ 0].dst  , myvar.msg.match[ 'in_port'  ]  )
            self.mappingof_mac_and_port[  format (  myvar.msg.datapath.id  , "d"  ).zfill( 16  ) ][  packet.Packet( myvar.msg.data ).get_protocols(  ethernet.ethernet )[ 0 ].src ] = myvar.msg.match[ 'in_port'  ]
            if  packet.Packet( myvar.msg.data ).get_protocols(  ethernet.ethernet )[ 0 ].dst in self.mappingof_mac_and_port[ format( myvar.msg.datapath.id  , "d" ).zfill( 16 ) ]  :
                 lerrned_seq_no   =    self.mappingof_mac_and_port[ format(  myvar.msg.datapath.id   , "d" ).zfill( 16  ) ][  packet.Packet(   myvar.msg.data ).get_protocols(  ethernet.ethernet )[ 0 ].dst ]
            else:
                 lerrned_seq_no   = myvar.msg.datapath.ofproto.OFPP_FLOOD

            taken_step = [myvar.msg.datapath.ofproto_parser.OFPActionOutput(lerrned_seq_no)]

            if  lerrned_seq_no  !=     myvar.msg.datapath.ofproto.OFPP_FLOOD :
                  similarity   =      myvar.msg.datapath.ofproto_parser.OFPMatch(  in_port  =   myvar.msg.match[ 'in_port'  ]  , eth_dst =  packet.Packet( myvar.msg.data ).get_protocols( ethernet.ethernet  )[ 0 ].dst    ,    eth_src =   packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src  )
                  if  myvar.msg.buffer_id   ==   myvar.msg.datapath.ofproto.OFP_NO_BUFFER:
                      self.introduce_data_transfer(  myvar.msg.datapath   ,   1 ,   similarity ,   taken_step )  
                  else:
                      self.introduce_data_transfer( myvar.msg.datapath  ,   1 ,  similarity    ,  taken_step  , myvar.msg.buffer_id )
                      return
            if   myvar.msg.buffer_id    ==   myvar.msg.datapath.ofproto.OFP_NO_BUFFER :
                   tmpval   =   myvar.msg.data 
            # Prepare the packet and send  
            finalpacket  = myvar.msg.datapath.ofproto_parser.OFPPacketOut(  datapath = myvar.msg.datapath  ,  buffer_id   = myvar.msg.buffer_id ,  in_port  =myvar.msg.match[ 'in_port' ] ,  actions =  taken_step ,   data =  tmpval )   
            myvar.msg.datapath.send_msg(  finalpacket )  
            
           
