### controler_hub
mininet> iperf h5 h1
*** Iperf: testing TCP bandwidth between h5 and h1 
*** Results: ['29.8 Mbits/sec', '29.2 Mbits/sec']
mininet> iperf h1 h5
*** Iperf: testing TCP bandwidth between h1 and h5 
*** Results: ['28.8 Mbits/sec', '28.2 Mbits/sec']

mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 h4 h5 
h2 -> h1 h3 h4 h5 
h3 -> h1 h2 h4 h5 
h4 -> h1 h2 h3 h5 
h5 -> h1 h2 h3 h4 
*** Results: 0% dropped (20/20 received)
mininet> dpctl dump-flows
*** s1 ------------------------------------------------------------------------
 cookie=0x0, duration=493.552s, table=0, n_packets=42449, n_bytes=54185299, priority=0 actions=CONTROLLER:65535
*** s2 ------------------------------------------------------------------------
 cookie=0x0, duration=493.557s, table=0, n_packets=43216, n_bytes=54235917, priority=0 actions=CONTROLLER:65535

mininet> h1 ping -c 3 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=130 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=62.3 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=65.0 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 62.296/85.723/129.847/31.219 ms
mininet> h1 ping -c 3 h3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=129 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=62.4 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=66.2 ms

--- 10.0.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2000ms
rtt min/avg/max/mdev = 62.365/85.948/129.303/30.695 ms
mininet> h1 ping -c 3 h4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=216 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=107 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=106 ms

--- 10.0.0.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 106.446/143.146/215.592/51.228 ms
mininet> h1 ping -c 3 h5
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
64 bytes from 10.0.0.5: icmp_seq=1 ttl=64 time=216 ms
64 bytes from 10.0.0.5: icmp_seq=2 ttl=64 time=108 ms
64 bytes from 10.0.0.5: icmp_seq=3 ttl=64 time=107 ms

--- 10.0.0.5 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 106.988/143.464/215.659/51.050 ms
mininet> h2 ping -c 3 h1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=62.8 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=62.4 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=66.6 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2004ms
rtt min/avg/max/mdev = 62.415/63.917/66.551/1.868 ms
mininet> h2 ping -c 3 h3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=131 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=62.9 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=66.5 ms

--- 10.0.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 62.881/86.846/131.170/31.376 ms
mininet> h2 ping -c 3 h4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=221 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=108 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=108 ms

--- 10.0.0.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2000ms
rtt min/avg/max/mdev = 108.061/145.908/221.293/53.305 ms
mininet> h2 ping -c 3 h5
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
64 bytes from 10.0.0.5: icmp_seq=1 ttl=64 time=219 ms
64 bytes from 10.0.0.5: icmp_seq=2 ttl=64 time=107 ms
64 bytes from 10.0.0.5: icmp_seq=3 ttl=64 time=108 ms

--- 10.0.0.5 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 107.172/144.637/218.988/52.574 ms
mininet> h3 ping -c 3 h1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=64.1 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=67.1 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=67.7 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 64.102/66.302/67.721/1.577 ms
mininet> h3 ping -c 3 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=63.0 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=63.0 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=67.1 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 62.996/64.384/67.130/1.941 ms
mininet> h3 ping -c 3 h4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=221 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=106 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=108 ms

--- 10.0.0.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 106.011/145.033/220.970/53.702 ms
mininet> h3 ping -c 3 h5
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
64 bytes from 10.0.0.5: icmp_seq=1 ttl=64 time=213 ms
64 bytes from 10.0.0.5: icmp_seq=2 ttl=64 time=108 ms
64 bytes from 10.0.0.5: icmp_seq=3 ttl=64 time=108 ms

--- 10.0.0.5 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 107.641/142.886/213.140/49.676 ms
mininet> h4 ping -c 3 h1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=109 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=104 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=107 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 104.292/106.771/109.071/1.955 ms
mininet> h4 ping -c 3 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=108 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=110 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=112 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2001ms
rtt min/avg/max/mdev = 108.411/110.290/112.242/1.564 ms
mininet> h4 ping -c 3 h3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=109 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=106 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=108 ms

--- 10.0.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 105.534/107.651/108.941/1.509 ms
mininet> h4 ping -c 3 h5
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
64 bytes from 10.0.0.5: icmp_seq=1 ttl=64 time=292 ms
64 bytes from 10.0.0.5: icmp_seq=2 ttl=64 time=144 ms
64 bytes from 10.0.0.5: icmp_seq=3 ttl=64 time=145 ms

--- 10.0.0.5 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 144.049/193.512/291.626/69.377 ms
mininet> h5 ping -c 3 h1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=108 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=112 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=110 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2004ms
rtt min/avg/max/mdev = 107.695/109.907/111.538/1.621 ms
mininet> h5 ping -c 3 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=108 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=105 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=108 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 104.968/106.960/108.107/1.414 ms
mininet> h5 ping -c 3 h3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=105 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=104 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=108 ms

--- 10.0.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 104.311/105.662/107.764/1.506 ms
mininet> h5 ping -c 3 h4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=145 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=145 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=145 ms

--- 10.0.0.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 144.909/145.089/145.213/0.130 ms


#learning_switch
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 h4 h5 
h2 -> h1 h3 h4 h5 
h3 -> h1 h2 h4 h5 
h4 -> h1 h2 h3 h5 
h5 -> h1 h2 h3 h4 
*** Results: 0% dropped (20/20 received)
mininet> dpctl dump-flows
*** s1 ------------------------------------------------------------------------
 cookie=0x0, duration=6.354s, table=0, n_packets=15, n_bytes=1078, idle_timeout=60, priority=1,dl_dst=ea:b8:48:e9:83:29 actions=output:"s1-eth1"
 cookie=0x0, duration=6.321s, table=0, n_packets=12, n_bytes=896, idle_timeout=60, priority=1,dl_dst=da:c0:d2:9e:7c:60 actions=output:"s1-eth2"
 cookie=0x0, duration=4.844s, table=0, n_packets=7, n_bytes=518, idle_timeout=60, priority=1,dl_dst=e6:b5:27:5b:68:2a actions=output:"s1-eth3"
 cookie=0x0, duration=4.811s, table=0, n_packets=5, n_bytes=378, idle_timeout=60, priority=1,dl_dst=5a:76:8f:ba:59:38 actions=output:"s1-eth4"
 cookie=0x0, duration=10.492s, table=0, n_packets=65, n_bytes=6298, priority=0 actions=CONTROLLER:65535
*** s2 ------------------------------------------------------------------------
 cookie=0x0, duration=6.054s, table=0, n_packets=7, n_bytes=518, idle_timeout=60, priority=1,dl_dst=ea:b8:48:e9:83:29 actions=output:"s2-eth3"
 cookie=0x0, duration=6.017s, table=0, n_packets=9, n_bytes=770, idle_timeout=60, priority=1,dl_dst=5a:76:8f:ba:59:38 actions=output:"s2-eth1"
 cookie=0x0, duration=5.419s, table=0, n_packets=5, n_bytes=434, idle_timeout=60, priority=1,dl_dst=da:c0:d2:9e:7c:60 actions=output:"s2-eth3"
 cookie=0x0, duration=4.854s, table=0, n_packets=5, n_bytes=434, idle_timeout=60, priority=1,dl_dst=e6:b5:27:5b:68:2a actions=output:"s2-eth3"
 cookie=0x0, duration=10.499s, table=0, n_packets=57, n_bytes=5598, priority=0 actions=CONTROLLER:65535
mininet> 

mininet> iperf h1 h5
*** Iperf: testing TCP bandwidth between h1 and h5 
*** Results: ['35.7 Mbits/sec', '35.1 Mbits/sec']
mininet> iperf h5 h1
*** Iperf: testing TCP bandwidth between h5 and h1 
*** Results: ['35.5 Mbits/sec', '34.9 Mbits/sec']


mininet> h1 ping -c 3 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=132 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=60.2 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=60.5 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 60.196/84.257/132.048/33.793 ms
mininet> h1 ping -c 3 h3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=127 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=61.8 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=62.2 ms

--- 10.0.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 61.783/83.677/127.030/30.655 ms
mininet> h1 ping -c 3 h4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=216 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=102 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=104 ms

--- 10.0.0.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2001ms
rtt min/avg/max/mdev = 102.454/140.881/216.190/53.255 ms
mininet> h1 ping -c 3 h5
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
64 bytes from 10.0.0.5: icmp_seq=1 ttl=64 time=210 ms
64 bytes from 10.0.0.5: icmp_seq=2 ttl=64 time=107 ms
64 bytes from 10.0.0.5: icmp_seq=3 ttl=64 time=107 ms

--- 10.0.0.5 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 106.752/141.048/209.575/48.455 ms
mininet> h2 ping -c 3 h1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=63.8 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=60.3 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=60.4 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2001ms
rtt min/avg/max/mdev = 60.316/61.520/63.803/1.614 ms
mininet> h2 ping -c 3 h3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=125 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=62.0 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=64.2 ms

--- 10.0.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 61.969/83.832/125.356/29.375 ms
mininet> h2 ping -c 3 h4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=212 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=102 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=104 ms

--- 10.0.0.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 102.242/139.540/212.462/51.567 ms
mininet> h2 ping -c 3 h5
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
64 bytes from 10.0.0.5: icmp_seq=1 ttl=64 time=211 ms
64 bytes from 10.0.0.5: icmp_seq=2 ttl=64 time=102 ms
64 bytes from 10.0.0.5: icmp_seq=3 ttl=64 time=106 ms

--- 10.0.0.5 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 102.024/139.744/211.402/50.693 ms
mininet> h3 ping -c 3 h1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=62.1 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=61.6 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=62.9 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 61.638/62.227/62.940/0.538 ms
mininet> h3 ping -c 3 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=63.1 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=61.7 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=62.0 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 61.738/62.290/63.120/0.597 ms
mininet> h3 ping -c 3 h4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=213 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=101 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=101 ms

--- 10.0.0.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 100.665/138.167/212.981/52.901 ms
mininet> h3 ping -c 3 h5
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
64 bytes from 10.0.0.5: icmp_seq=1 ttl=64 time=211 ms
64 bytes from 10.0.0.5: icmp_seq=2 ttl=64 time=103 ms
64 bytes from 10.0.0.5: icmp_seq=3 ttl=64 time=106 ms

--- 10.0.0.5 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 102.888/140.133/211.110/50.208 ms
mininet> h4 ping -c 3 h1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=103 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=100 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=100 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 100.355/101.213/102.875/1.175 ms
mininet> h4 ping -c 3 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=101 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=100 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=100 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 100.277/100.688/101.472/0.554 ms
mininet> h4 ping -c 3 h3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=101 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=100 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=100 ms

--- 10.0.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 100.322/100.610/101.154/0.384 ms
mininet> h4 ping -c 3 h5
PING 10.0.0.5 (10.0.0.5) 56(84) bytes of data.
64 bytes from 10.0.0.5: icmp_seq=1 ttl=64 time=287 ms
64 bytes from 10.0.0.5: icmp_seq=2 ttl=64 time=144 ms
64 bytes from 10.0.0.5: icmp_seq=3 ttl=64 time=144 ms

--- 10.0.0.5 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2004ms
rtt min/avg/max/mdev = 144.032/191.698/286.618/67.118 ms
mininet> h5 ping -c 3 h1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=107 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=106 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=105 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 104.803/105.961/106.817/0.849 ms
mininet> h5 ping -c 3 h2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=103 ms
64 bytes from 10.0.0.2: icmp_seq=2 ttl=64 time=103 ms
64 bytes from 10.0.0.2: icmp_seq=3 ttl=64 time=103 ms

--- 10.0.0.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 102.723/102.914/103.120/0.162 ms
mininet> h5 ping -c 3 h3
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=105 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=103 ms

64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=103 ms

--- 10.0.0.3 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2001ms
rtt min/avg/max/mdev = 102.584/103.402/104.844/1.022 ms
mininet> h5 ping -c 3 h4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=144 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=144 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=142 ms

--- 10.0.0.4 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 141.983/143.265/143.932/0.906 ms



#### Firewall + monitor #########

mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 X h5 
h2 -> h1 X h4 h5 
h3 -> h1 X h4 X 
h4 -> X h2 h3 h5 
h5 -> h1 h2 X h4 
*** Results: 30% dropped (14/20 received)
mininet> 

mininet> dpctl dump-flows
*** s1 ------------------------------------------------------------------------
 cookie=0x0, duration=135.826s, table=0, n_packets=155, n_bytes=12866, priority=0 actions=CONTROLLER:65535
*** s2 ------------------------------------------------------------------------
 cookie=0x0, duration=135.831s, table=0, n_packets=162, n_bytes=13216, priority=0 actions=CONTROLLER:65535


## counting packets on s1 from h3 
Sending packet out
Sending packet out
Sending packet out
Sending packet out
Sending packet out
Sending packet out
Sending packet out
Sending packet out
Counting packet from H3 on Switch S1. Total packets: 26