from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import ethernet
from simple_switch import SimpleSwitch
from utils import *

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(SCRIPT_PATH, "proxy.config")
FLOW_HARD_TIMEOUT = 30
FLOW_IDLE_TIMEOUT = 10

class ProxySwitch(SimpleSwitch):


    def __init__(self, *args, **kwargs):
        SimpleSwitch.__init__(self, *args, **kwargs)
        config = readConfigFile(config_file)
        self._serverip = config["general"]['server_ip']
        self._serverport = int(config["general"]['server_port'])
        self._proxyip_1 = config["general"]['proxy_ip_1']
        self._proxyport_1 = int(config["general"]['proxy_port_1'])
        self._source_1 = config["general"]['source_1']
        self._proxyip_2 = config["general"]['proxy_ip_2']
        self._proxyport_2 = int(config["general"]['proxy_port_2'])
        self._source_2 = config["general"]['source_2']

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath

        self.macLearningHandle(msg)

        if packetIsARP(msg) :
            self._handle_PacketInARP(ev)
            return

        if packetIsTCP(msg) :
            self._handle_PacketInTCP(ev)
            return
        SimpleSwitch._packet_in_handler(self, ev)

    def _handle_PacketInARP(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto	
        arppkt = None

        # If this an ARP Packet srcd at the server, 
        # Then we drop it not to confuse the MAC learning
        # At the hosts
        if packetArpSrcIp(msg, self._serverip):
           return

        # XXX If this is an ARP Request for the server iP
        # create new ARP request and save it in arppkt
        if packetIsRequestARP(msg) : 
            if packetArpDstIp(msg, self._serverip):
                arppkt = createArpRequest(msg, self._proxyip)
        
        # XXX If this is an ARP Reply from the proxy
        # create new ARP reply  and save it in arppkt
        if packetIsReplyARP(msg) : 
            if packetArpSrcIp(msg, self._proxyip):
                arppkt = createArpReply(msg, self._serverip)

        # If we haven't created a new arp packet, send the one we 
        # received
        if arppkt is None :
            SimpleSwitch._packet_in_handler(self, ev)
            return

        # Send a packet out with the ARP
        actions = [createOFAction(datapath, ofproto.OFPAT_OUTPUT, ofproto.OFPP_FLOOD)]
        
        sendPacketOut(msg=msg, actions=actions, data=arppkt.data)

    def _handle_PacketInTCP(self, ev):

        msg = ev.msg
        datapath = msg.datapath
        out_port = self.get_out_port(msg)
        ofproto = datapath.ofproto

        actions = []
        # XXX If packet is destined to serverip:server port
        # make the appropriate rewrite
        if packetDstIp(msg, self._serverip) : 
            if packetDstTCPPort(msg, self._serverport) :
                if packetSrcIp(msg, self._source_1) :
			         actions.append( createOFAction(datapath, ofproto.OFPAT_SET_TP_DST, self._proxyport_1 ) )
			         actions.append( createOFAction(datapath, ofproto.OFPAT_SET_NW_DST, self._proxyip_1 ) )
                else packetSrcIp(msg, self._source_2) :
                     actions.append( createOFAction(datapath, ofproto.OFPAT_SET_TP_DST, self._proxyport_2 ) )
                     actions.append( createOFAction(datapath, ofproto.OFPAT_SET_NW_DST, self._proxyip_2 ) )

        # XXX If packet is sourced at proxyip:proxy port
        # make the appropriate rewrite
        if packetSrcIp(msg, self._proxyip_1) :
		    if packetSrcTCPPort(msg, self._proxyport_1) :
			    actions.append( createOFAction(datapath, ofproto.OFPAT_SET_TP_SRC, self._serverport ) )
			    actions.append( createOFAction(datapath, ofproto.OFPAT_SET_NW_SRC, self._serverip ) )
        if packetSrcIp(msg, self._proxyip_2) :
            if packetSrcTCPPort(msg, self._proxyport_2) :
                actions.append( createOFAction(datapath, ofproto.OFPAT_SET_TP_SRC, self._serverport ) )
                actions.append( createOFAction(datapath, ofproto.OFPAT_SET_NW_SRC, self._serverip ) )
	
        actions.append( createOFAction(datapath, ofproto.OFPAT_OUTPUT, out_port))
        
        match = getFullMatch( msg )
        
        sendFlowMod(msg, match, actions, FLOW_HARD_TIMEOUT, FLOW_IDLE_TIMEOUT, msg.buffer_id)
