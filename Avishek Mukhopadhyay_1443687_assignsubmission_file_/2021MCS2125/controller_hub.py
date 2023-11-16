

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



###########################################################
#######  Class Name  ControllerHub                        #
#######  Purpose Implementation of HUB functionality      #
###########################################################


class ControllerHub(  app_manager.RyuApp ):
      #  1.3 oenflow version used
      OFP_VERSIONS  =   [  ofproto_v1_3.OFP_VERSION ]  
        

     
      def   __init__(  self , *firstlevelargs , **secondlevelargs ):
            super( ControllerHub     , self ).__init__(*firstlevelargs  , **secondlevelargs  )


      # data transfer or flow creation function
      def     introduce_data_transfer(self, routevar, precedence, similarity, jobs, buffer_id=None):

            anothervar = [  routevar.ofproto_parser.OFPInstructionActions(  routevar.ofproto.OFPIT_APPLY_ACTIONS ,  jobs )  ]   

            if   buffer_id   ==   None:
                 changedvalue   =  routevar.ofproto_parser.OFPFlowMod(    datapath =  routevar ,  priority =precedence,match = similarity, instructions = anothervar   )   

            else:
                 changedvalue  =   routevar.ofproto_parser.OFPFlowMod(  datapath = routevar, buffer_id  = buffer_id , priority=precedence  , match=similarity , instructions = anothervar )  

            routevar.send_msg(  changedvalue  )

      # This function configures the initial nature of the hub
      @set_ev_cls(  ofp_event.EventOFPSwitchFeatures , CONFIG_DISPATCHER  )
      def   function_for_switch(self , myvar ):     
            self.introduce_data_transfer( myvar.msg.datapath  , 0  , myvar.msg.datapath.ofproto_parser.OFPMatch() , [ myvar.msg.datapath.ofproto_parser.OFPActionOutput(  myvar.msg.datapath.ofproto.OFPP_CONTROLLER  , myvar.msg.datapath.ofproto.OFPCML_NO_BUFFER ) ]  )   




      # This function is called when ever a data backet is received
      @set_ev_cls(    ofp_event.EventOFPPacketIn  , MAIN_DISPATCHER  )   
      def   function_for_packet(self, myvar  ):  
            tmpval = None
            # Ignore link layer discovery packets
            if   packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].ethertype   ==  ether_types.ETH_TYPE_LLDP:
                 return
            self.logger.info("I have found packet with   %s    %s  %s   %s   "  ,  format(  myvar.msg.datapath.id , "d" ).zfill( 16  ) , packet.Packet(  myvar.msg.data  ).get_protocols( ethernet.ethernet )[ 0 ].src ,  packet.Packet(  myvar.msg.data ).get_protocols(  ethernet.ethernet )[ 0].dst  , myvar.msg.match[ 'in_port'  ]  )

            if   myvar.msg.buffer_id    ==   myvar.msg.datapath.ofproto.OFP_NO_BUFFER :
                   tmpval   =   myvar.msg.data 
            # Now the step  to be taken is FLOODING 
            # Prepare the packet and send
            finalpacket  = myvar.msg.datapath.ofproto_parser.OFPPacketOut(  datapath = myvar.msg.datapath  ,  buffer_id   = myvar.msg.buffer_id ,  in_port  =myvar.msg.match[ 'in_port' ] ,  actions =  [myvar.msg.datapath.ofproto_parser.OFPActionOutput( myvar.msg.datapath.ofproto.OFPP_FLOOD)] ,   data =  tmpval )   
            myvar.msg.datapath.send_msg(  finalpacket )  
            
           
