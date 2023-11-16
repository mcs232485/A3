from mininet.topo import Topo

class MyTopo( Topo ):

    def build( self ):
    
        h1 = self.addHost( 'h1' , ip='10.1.1.1', mac='00:00:00:00:00:10')
        h2 = self.addHost( 'h2' , ip='10.2.2.2', mac='00:00:00:00:00:20')
        h3 = self.addHost( 'h3' , ip='10.3.3.3', mac='00:00:00:00:00:30')
        h4 = self.addHost( 'h4' , ip='10.4.4.4', mac='00:00:00:00:00:40')
        h5 = self.addHost( 'h5' , ip='10.5.5.5', mac='00:00:00:00:00:50')
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )

        self.addLink( h1, s1 )
        self.addLink( h2, s1 )
        self.addLink( h3, s1 )
        self.addLink( s1, s2 )
        self.addLink( s2, h4 )
        self.addLink( s2, h5 )

topos = { 'mytopo': ( lambda: MyTopo() ) }