from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink, Link

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):
        info('*** Configuring hosts ')
        addr_r0 = ['10.0.0.1/24', '10.0.2.1/24']
        addr_r1 = ['10.0.1.1/24', '10.0.3.1/24']
        addr_h1 = ['10.0.0.100/24','10.0.1.100/24']
        addr_h2 = ['10.0.2.100/24','10.0.3.100/24']

#add routers
        r0 = self.addNode('r0', cls=LinuxRouter, ip=addr_r0[0])
        r1 = self.addNode('r1', cls=LinuxRouter, ip=addr_r1[0])

#add switches
        s1, s2, s3, s4 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3', 's4' ) ]

#link switches and routers
        self.addLink( s1, r0, cls=TCLink, bw=50, params2={ 'ip' : addr_r0[0] } )
        self.addLink( s2, r0, cls=TCLink, bw=50, intfName2='r0-eth1', params2={ 'ip' : addr_r0[1] } )
        self.addLink( s3, r1, cls=TCLink, bw=50, params2={ 'ip' : addr_r1[0] } )
        self.addLink( s4, r1, cls=TCLink, bw=50, intfName2='r1-eth1', params2={ 'ip' : addr_r1[1] } )

#add hosts
        info('*** Associating and Creating links')
        h1 = self.addHost( 'h1', ip=addr_h1[0] , defaultRoute='via 10.0.0.1' )
        h2 = self.addHost( 'h2', ip=addr_h2[0] , defaultRoute='via 10.0.2.1' )

#link switches and hosts
        self.addLink(h1, s1, cls=TCLink, bw=50, intfName1='h1-eth0')
        self.addLink(h1, s3, cls=TCLink, bw=50, intfName1='h1-eth1')
        self.addLink(h2, s2, cls=TCLink, bw=50, intfName1='h2-eth0')
        self.addLink(h2, s4, cls=TCLink, bw=50, intfName1='h2-eth1')

def configure_network(network):
    r0=network.get('r0')
    r1=network.get('r1')
    h1=network.get('h1')
    h2=network.get('h2')
    r0.setIP('10.0.2.1/24', intf='r0-eth1')
    r1.setIP('10.0.3.1/24', intf='r1-eth1')
    h1.setIP('10.0.1.100/24', intf='h1-eth1')
    h2.setIP('10.0.3.100/24', intf='h2-eth1')

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )  # controller is used by s1-s3
    configure_network(net)
    net.start()
    info( '*** Routing Table on Router:\n' )
    info( net[ 'r0' ].cmd( 'route' ) )
    info( net[ 'r1' ].cmd( 'route' ) )
    net.pingAll()
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

