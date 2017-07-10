#!/usr/bin/env python
"""Create streams and receive packets"""
# pylint: disable=E1101

import inspect
import pprint
import sys
import time
import ipaddress
from ostinato.core import ost_pb, DroneProxy
from ostinato.protocols.mac_pb2 import mac
from ostinato.protocols.eth2_pb2 import eth2
from ostinato.protocols.ip4_pb2 import ip4
from ostinato.protocols.udp_pb2 import udp
from ostinato.protocols.igmp_pb2 import igmp

IGMPv2_REQUEST = 0x16

DEBUG = False
PP = pprint.PrettyPrinter(indent=4)


def dbg_print(args):
    """Print debug messages if they are enabled"""
    if DEBUG:
        print args

def get_class_from_frame(fr):
    """Return the class a method was called from"""
    args, _, _, value_dict = inspect.getargvalues(fr)
    # we check the first parameter for the frame function is
    # named 'self'
    if len(args) and args[0] == 'self':
        # in that case, 'self' will be referenced in value_dict
        instance = value_dict.get('self', None)
        if instance:
            # return its class
            return getattr(instance, '__class__', None)
        # return None otherwise
    return None

class Traffic(object):
    """Class for traffic streams"""
    def __init__(self):
        self.drone = DroneProxy('127.0.0.1')
        self.drone.connect()

        self.port_id_list = self.drone.getPortIdList()
        self.port_config_list = self.drone.getPortConfig(self.port_id_list)
        self.tx_port = ost_pb.PortIdList()
        self.rx_port = ost_pb.PortIdList()
        self.interfaces = self._getInterfaces()
        self.addedInterfaces = []
        self.tx_stats = None

    def __del__(self):
        """Cleanup the streams"""
        for interface in self.interfaces:
            self.drone.deleteStream(interface['stream_id_list'])
        self.drone.disconnect()

    def _getInterfaces(self):
        """Create a list of interface dicts which can be used for streams"""
        interfaces = []
        for port in self.port_config_list.port:
            stream_id_list = ost_pb.StreamIdList()
            stream_id_list.stream_id.add().id = 1
            stream_id_list.stream_id.add().id = 2
            stream_id_list.stream_id.add().id = 3
            stream_id_list.stream_id.add().id = 4
            stream_id_list.stream_id.add().id = 5
            stream_id_list.port_id.id = port.port_id.id
            self.drone.addStream(stream_id_list)
            stream_cfg = ost_pb.StreamConfigList()
            stream_cfg.port_id.id = port.port_id.id

            interface = {
                'name': port.name,
                'port_id': port.port_id,
                'port_id_id': port.port_id.id,
                'stream_id_list': stream_id_list,
                'stream_cfg': stream_cfg,
                'stream_id': 1,
            }
            interfaces.append(interface)
        return interfaces

    def _cleanupRun(self):
        """Delete all current streams, so that we can create new
           once for the next run"""
        for interface in self.interfaces:
            stream_id_list = interface['stream_id_list']
            port_id = interface['port_id_id']
            self.drone.deleteStream(stream_id_list)
            self.drone.addStream(stream_id_list)
            stream_cfg = ost_pb.StreamConfigList()
            stream_cfg.port_id.id = port_id
            interface['stream_cfg'] = stream_cfg
            interface['stream_id'] = 1

    def _getInterfaceByName(self, interface_name):
        """Return the interface dict for a given interface name"""
        for interface in self.interfaces:
            if interface['name'] == interface_name:
                return interface
        raise NameError('getInterface called for unknown interface name')

    def _getInterfaceByPortId(self, port_id):
        """Return the interface dict for a given interface name"""
        for interface in self.interfaces:
            if interface['port_id_id'] == port_id:
                return interface
        raise NameError('getInterface called for unknown interface name')

    def _getInterfaceId(self, interface_name):
        """Return the Ostinato ID for an interface name"""
        for interface in self.interfaces:
            if interface['name'] == interface_name:
                return interface['port_id_id']
        raise NameError('getInterfaceId called for unknown interface {0}'.
                        format(interface_name))

    def getInterfaceNames(self):
        """Return a list of interface names which can be used for streams"""
        return [interface['name'] for interface in self.interfaces]

    def addInterface(self, interface_name):
        """Add an interface to the configuration. It will then be used for
           transmit and receive"""
        dbg_print('addInterface({0})'.format(interface_name))
        self.addedInterfaces.append(interface_name)
        port_id = self._getInterfaceId(interface_name)
        self.rx_port.port_id.add().id = port_id
        self.tx_port.port_id.add().id = port_id

    def _getInterfaceMacAddress(self, interface):
        """Return the MAC address of an interface"""
        return 0x001020304000 + interface['port_id_id']

    def _getInterfaceIPAddress(self, interface):
        """Return the IP address of an interface"""
        return 0xc0a83a0a + interface['port_id_id']

    def _addEthernetHeader(self, stream, src_mac, dst_mac):
        """Add an Ethernet header to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kMacFieldNumber
        proto.Extensions[mac].src_mac = src_mac
        proto.Extensions[mac].dst_mac = dst_mac

    def _addEthertypeIP(self, stream):
        """Add an Ethernet Type header for IP to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kEth2FieldNumber
        proto.Extensions[eth2].type = 0x0800
        proto.Extensions[eth2].is_override_type = True

    def _addIPHeader(self, stream, src_ip, dst_ip):
        """Add an IP header to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kIp4FieldNumber
        proto.Extensions[ip4].src_ip = src_ip
        proto.Extensions[ip4].dst_ip = dst_ip

    def _addUdpHeader(self, stream, src_port, dst_port):
        """Add a UDP header to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kUdpFieldNumber
        proto.Extensions[udp].is_override_src_port = True
        proto.Extensions[udp].is_override_dst_port = True
        proto.Extensions[udp].src_port = src_port
        proto.Extensions[udp].dst_port = dst_port

    def _addIGMPHeader(self, stream, igmp_type, group):
        """Add an IGMP header to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kIgmpFieldNumber
        proto.Extensions[igmp].type = igmp_type
        proto.Extensions[igmp].group_address.v4 = group

    def _addIGMPRequestHeader(self, stream, group):
        """Add an IGMP Request header to a stream"""
        self._addIGMPHeader(stream, IGMPv2_REQUEST, group)

    def _addStream(self, stream_cfg, interface, num_packets, packets_per_sec):
        """Add a stream to an interface, and return it"""
        stream = stream_cfg.stream.add()
        stream.stream_id.id = interface['stream_id']
        interface['stream_id'] = interface['stream_id'] + 1
        stream.core.is_enabled = True
        stream.core.frame_len = 128
        stream.control.num_packets = num_packets
        stream.control.packets_per_sec = packets_per_sec
        return stream

    def _addUDPPacketStream(self, stream, src_mac, dst_mac, src_ip, dst_ip):
        """Add a UDP packets to a stream"""
        self._addEthernetHeader(stream, src_mac=src_mac,
                                dst_mac=dst_mac)
        self._addEthertypeIP(stream)
        self._addIPHeader(stream, src_ip=src_ip, dst_ip=dst_ip)
        self._addUdpHeader(stream, 0x1234, 0x4321)

        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kPayloadFieldNumber

    def addUDPStream(self, src_interface_name, dst_interface_name,
                     num_packets, packets_per_sec):
        """Add a UDP stream from the source interface to the destination
           interface"""
        dbg_print('addUDPStream({0} {1} {2} {3})'.format(src_interface_name,
                                                         dst_interface_name,
                                                         num_packets,
                                                         packets_per_sec))
        src_interface = self._getInterfaceByName(src_interface_name)
        dst_interface = self._getInterfaceByName(dst_interface_name)
        stream_cfg = src_interface['stream_cfg']
        stream = self._addStream(stream_cfg, src_interface, num_packets,
                                 packets_per_sec)
        src_mac = self._getInterfaceMacAddress(src_interface)
        dst_mac = self._getInterfaceMacAddress(dst_interface)
        src_ip = self._getInterfaceIPAddress(src_interface)
        dst_ip = self._getInterfaceIPAddress(dst_interface)

        self._addUDPPacketStream(stream, src_mac, dst_mac, src_ip, dst_ip)
        self.drone.modifyStream(stream_cfg)

    def addUDPBroadcastStream(self, src_interface_name, num_packets,
                              packets_per_sec):
        """Add a UDP broadcast stream from the source interface to the
           broadcast address"""
        dbg_print('addUDPBroadcastStream({0} {1} {2})'.
                  format(src_interface_name,
                         num_packets,
                         packets_per_sec))
        src_interface = self._getInterfaceByName(src_interface_name)
        stream_cfg = src_interface['stream_cfg']
        stream = self._addStream(stream_cfg, src_interface, num_packets,
                                 packets_per_sec)
        src_mac = self._getInterfaceMacAddress(src_interface)
        dst_mac = 0xffffffffffff
        src_ip = self._getInterfaceIPAddress(src_interface)
        dst_ip = 0xc0a82aff

        self._addUDPPacketStream(stream, src_mac, dst_mac, src_ip, dst_ip)
        self.drone.modifyStream(stream_cfg)

    def addUDPMulticastStream(self, src_interface_name, group_str, num_packets,
                              packets_per_sec):
        """Add a UDP multicast stream from the source interface to the
           group address"""
        dbg_print('addUDPMulticastStream({0} {1} {2} {3})'.
                  format(src_interface_name,
                         group_str,
                         num_packets,
                         packets_per_sec))
        src_interface = self._getInterfaceByName(src_interface_name)
        stream_cfg = src_interface['stream_cfg']
        stream = self._addStream(stream_cfg, src_interface, num_packets,
                                 packets_per_sec)
        src_mac = self._getInterfaceMacAddress(src_interface)
        group = ipaddress.ip_address(group_str.decode())
        dst_mac = 0x01005e000000 + (int(group) & 0x07fffff)
        src_ip = self._getInterfaceIPAddress(src_interface)
        dst_ip = int(group)

        self._addUDPPacketStream(stream, src_mac, dst_mac, src_ip, dst_ip)
        self.drone.modifyStream(stream_cfg)

    def addIGMPRequestStream(self, src_interface_name, group, num_packets,
                             packets_per_sec):
        """Add a IGMP request stream from the source interface to the
           group address"""
        dbg_print('addIGMPStream({0} {1} {2})'.
                  format(src_interface_name, group, num_packets))
        src_interface = self._getInterfaceByName(src_interface_name)
        stream_cfg = src_interface['stream_cfg']
        stream = self._addStream(stream_cfg, src_interface, num_packets,
                                 packets_per_sec)
        src_mac = self._getInterfaceMacAddress(src_interface)
        dst_mac = 0x01005e00001
        src_ip = self._getInterfaceIPAddress(src_interface)
        dst_ip = group

        self._addEthernetHeader(stream, src_mac=src_mac,
                                dst_mac=dst_mac)
        self._addEthertypeIP(stream)
        self._addIPHeader(stream, src_ip=src_ip, dst_ip=dst_ip)
        self._addIGMPRequestHeader(stream, group)

        self.drone.modifyStream(stream_cfg)

    def learningStream(self, interface_name):
        """Create a stream on the interface for bridge learning. Two broadcast
           packets will be sent, so allowing the switch to learn the source
           MAC address on the interface."""
        dbg_print('learningStream({0})'.format(interface_name))
        self.addUDPBroadcastStream(interface_name, 2, 1)

    def learning(self):
        """Perform learning on each port, by sending a couple of packet,
           so that the bridge learns the address on the interface"""
        dbg_print('learning')
        for interface_name in self.addedInterfaces:
            self.learningStream(interface_name)
        frame = inspect.stack()[1][0]
        method = inspect.stack()[1][3]
        test = get_class_from_frame(frame).__name__
        self._run(test, method)

    def _saveCapture(self, testname, methodname, interface_name):
        """Save the capture file for one interface"""
        filename = "{0}-{1}-{2}.pcap".format(testname, methodname,
                                             interface_name)
        interface = self._getInterfaceByName(interface_name)
        buff = self.drone.getCaptureBuffer(interface['port_id'])
        self.drone.saveCaptureBuffer(buff, filename)

    def _saveCaptures(self, testname, methodname):
        """Save the capture files, using the test name as a prefix"""
        for interface_name in self.addedInterfaces:
            self._saveCapture(testname, methodname, interface_name)

    def _run(self, test, method):
        """Do the real work"""
        self.drone.clearStats(self.tx_port)
        self.drone.clearStats(self.rx_port)
        self.drone.startCapture(self.rx_port)
        self.drone.startTransmit(self.tx_port)

        done = False
        while not done:
            done = True
            tx_stats = self.drone.getStats(self.tx_port)
            for port_stats in tx_stats.port_stats:
                if port_stats.state.is_transmit_on:
                    done = False
            time.sleep(1)

        self.drone.stopTransmit(self.tx_port)
        self.drone.stopCapture(self.rx_port)
        self.tx_stats = self.drone.getStats(self.tx_port)
        self._saveCaptures(test, method)
        self._cleanupRun()

    def run(self):
        """Run the streams"""
        dbg_print('run')
        frame = inspect.stack()[1][0]
        method = inspect.stack()[1][3]
        test = get_class_from_frame(frame).__name__
        self._run(test, method)

    def getStats(self, interface_name):
        """Return the interface statistics"""
        dbg_print('getStats({0})'.format(interface_name))
        port_id = self._getInterfaceId(interface_name)
        for port_stats in self.tx_stats.port_stats:
            if port_stats.port_id.id == port_id:
                stats = {
                    'rx_pkts': port_stats.rx_pkts,
                    'rx_bytes': port_stats.rx_bytes,
                    'rx_pps': port_stats.rx_pps,
                    'rx_bps': port_stats.rx_bps,
                    'tx_pkts': port_stats.tx_pkts,
                    'tx_bytes': port_stats.tx_bytes,
                    'tx_pps': port_stats.tx_pps,
                    'tx_bps': port_stats.tx_bps,
                    'rx_drops': port_stats.rx_drops,
                    'rx_errors': port_stats.rx_errors,
                    'rx_fifo_errors': port_stats.rx_fifo_errors,
                    'rx_frame_errors': port_stats.rx_frame_errors,
                }
                return stats


if __name__ == '__main__':
    try:
        traffic = Traffic()
        print traffic.getInterfaceNames()
        traffic.addInterface('eth10')
        traffic.addInterface('eth11')
        traffic.addInterface('eth12')
        traffic.addInterface('eth13')
        traffic.addInterface('eth14')
        traffic.addInterface('eth15')
        traffic.addInterface('eth16')
        traffic.addInterface('eth17')
        traffic.learning()
        print traffic.getStats('eth10')
        print traffic.getStats('eth11')
        traffic.addUDPStream('eth10', 'eth11', 100, 10)
        traffic.addUDPStream('eth11', 'eth10', 50, 5)
        traffic.run()
        print 'Statistics for eth10: {0}'.format(traffic.getStats('eth10'))
        print 'Statistics for eth11: {0}'.format(traffic.getStats('eth11'))
    except KeyboardInterrupt, e:
        sys.exit(1)
