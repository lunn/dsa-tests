#!/usr/bin/env python
"""Create streams and receive packets"""
# pylint: disable=E1101

import inspect
import pprint
import sys
import time
import ipaddress
import netaddr
from ostinato.core import ost_pb, DroneProxy
from ostinato.protocols.mac_pb2 import mac, Mac
from ostinato.protocols.eth2_pb2 import eth2
from ostinato.protocols.ip4_pb2 import ip4
from ostinato.protocols.ip6_pb2 import ip6
from ostinato.protocols.udp_pb2 import udp
from ostinato.protocols.igmp_pb2 import igmp
from ostinato.protocols.sign_pb2 import sign

IGMPv2_REQUEST = 0x16

DEBUG = False
PP = pprint.PrettyPrinter(indent=4)


def dbg_print(args):
    """Print debug messages if they are enabled"""
    if DEBUG:
        print args


def get_class_from_frame(frame):
    """Return the class a method was called from"""
    args, _, _, value_dict = inspect.getargvalues(frame)
    # we check the first parameter for the frame function is
    # named 'self'
    if args and args[0] == 'self':
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
        self.stream_stats = None
        self.guids = ost_pb.StreamGuidList()
        self.port_config = ost_pb.PortConfigList()
        self.port_config_ports = 0
        self.guid = 0

    def __del__(self):
        """Cleanup the streams"""
        for interface in self.interfaces:
            for stream_id_list in interface['stream_id_list_list']:
                self.drone.deleteStream(stream_id_list)
        self.drone.disconnect()

    def _getInterfaces(self):
        """Create a list of interface dicts which can be used for streams"""
        interfaces = []
        for port in self.port_config_list.port:
            stream_cfg = ost_pb.StreamConfigList()
            stream_cfg.port_id.id = port.port_id.id

            interface = {
                'name': port.name,
                'port_id': port.port_id,
                'port_id_id': port.port_id.id,
                'stream_id_list_list': [],
                'stream_cfg': stream_cfg,
                'stream_id': 1,
            }
            interfaces.append(interface)
        return interfaces

    def _cleanupRun(self):
        """Delete all current streams, so that we can create new
           once for the next run"""
        for interface in self.interfaces:
            port_id = interface['port_id_id']
            for stream_id_list in interface['stream_id_list_list']:
                self.drone.deleteStream(stream_id_list)
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
        self.guids.port_id_list.port_id.add().id = port_id
        self.port_config.port.add().port_id.id = port_id
        self.port_config.port[self.port_config_ports] \
                        .is_tracking_stream_stats = True
        self.port_config_ports += 1

    def _getInterfaceMacAddress(self, interface):
        """Return the MAC address of an interface"""
        return 0x001020304000 + interface['port_id_id']

    def getInterfaceMacAddress(self, interface_name):
        """Get the MAC address being used on the interface"""
        interface = self._getInterfaceByName(interface_name)
        number = self._getInterfaceMacAddress(interface)
        eui = netaddr.EUI(number)
        eui.dialect = netaddr.mac_unix_expanded
        return str(eui)

    def _getInterfaceIPv4Address(self, interface):
        """Return the IPv4 address of an interface"""
        return 0xc0a83a0a + interface['port_id_id']

    def _getInterfaceIPv6Address(self, interface):
        """Return the IPv6 address of an interface"""
        ipv6 = {'hi': 0xfd42424200000000,
                'lo': 0x10 + interface['port_id_id']}
        return ipv6

    def _addEthernetHeader(self, stream, src_mac, dst_mac, src_mac_count=0,
                           src_mac_step=1):
        """Add an Ethernet header to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kMacFieldNumber
        proto.Extensions[mac].src_mac = src_mac
        proto.Extensions[mac].dst_mac = dst_mac
        if src_mac_count:
            proto.Extensions[mac].src_mac_mode = Mac.e_mm_inc
            proto.Extensions[mac].src_mac_count = src_mac_count
            proto.Extensions[mac].src_mac_step = src_mac_step

    def _addEthertypeIPv4(self, stream):
        """Add an Ethernet Type header for IPv4 to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kEth2FieldNumber
        proto.Extensions[eth2].type = 0x0800
        proto.Extensions[eth2].is_override_type = True

    def _addEthertypeIPv6(self, stream):
        """Add an Ethernet Type header for IPv6 to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kEth2FieldNumber
        proto.Extensions[eth2].type = 0x86dd
        proto.Extensions[eth2].is_override_type = True

    def _addIPv4Header(self, stream, src_ip, dst_ip):
        """Add an IPv4 header to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kIp4FieldNumber
        proto.Extensions[ip4].src_ip = src_ip
        proto.Extensions[ip4].dst_ip = dst_ip

    def _addIPv6Header(self, stream, src_ip, dst_ip):
        """Add an IPv6 header to a stream"""
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kIp6FieldNumber
        proto.Extensions[ip6].src_addr_hi = src_ip['hi']
        proto.Extensions[ip6].src_addr_lo = src_ip['lo']
        proto.Extensions[ip6].dst_addr_hi = dst_ip['hi']
        proto.Extensions[ip6].dst_addr_lo = dst_ip['lo']

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
        stream_id_list = ost_pb.StreamIdList()
        stream_id_list.stream_id.add().id = interface['stream_id']
        stream_id_list.port_id.id = interface['port_id_id']
        self.drone.addStream(stream_id_list)
        interface['stream_id_list_list'].append(stream_id_list)
        stream = stream_cfg.stream.add()
        stream.stream_id.id = interface['stream_id']
        interface['stream_id'] = interface['stream_id'] + 1
        stream.core.is_enabled = True
        stream.core.frame_len = 128
        stream.control.num_packets = num_packets
        stream.control.packets_per_sec = packets_per_sec
        return stream

    def _addUDPv4PacketStream(self, stream, src_mac, src_mac_count,
                              src_mac_step, dst_mac, src_ip, dst_ip):
        """Add a UDPv4 packets to a stream"""
        self._addEthernetHeader(stream, src_mac=src_mac,
                                dst_mac=dst_mac,
                                src_mac_count=src_mac_count,
                                src_mac_step=src_mac_step)
        self._addEthertypeIPv4(stream)
        self._addIPv4Header(stream, src_ip=src_ip, dst_ip=dst_ip)
        self._addUdpHeader(stream, 0x1234, 0x4321)

        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kPayloadFieldNumber
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kSignFieldNumber
        proto.Extensions[sign].stream_guid = self.guid
        self.guid += 1

    def _addUDPv6PacketStream(self, stream, src_mac, src_mac_count,
                              src_mac_step, dst_mac, src_ip, dst_ip):
        """Add a UDPv6 packets to a stream"""
        self._addEthernetHeader(stream, src_mac=src_mac,
                                dst_mac=dst_mac,
                                src_mac_count=src_mac_count,
                                src_mac_step=src_mac_step)
        self._addEthertypeIPv6(stream)
        self._addIPv6Header(stream, src_ip=src_ip, dst_ip=dst_ip)
        self._addUdpHeader(stream, 0x1234, 0x4321)

        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kPayloadFieldNumber
        proto = stream.protocol.add()
        proto.protocol_id.id = ost_pb.Protocol.kSignFieldNumber
        proto.Extensions[sign].stream_guid = self.guid
        self.guid += 1

    def addUDPStream(self, src_interface_name, dst_interface_name,
                     num_packets, packets_per_sec):
        """Add a UDPv4 stream from the source interface to the destination
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
        src_ip = self._getInterfaceIPv4Address(src_interface)
        dst_ip = self._getInterfaceIPv4Address(dst_interface)

        self._addUDPv4PacketStream(stream, src_mac, 0, 1, dst_mac, src_ip,
                                   dst_ip)
        self.drone.modifyStream(stream_cfg)

    def addUDPv6Stream(self, src_interface_name, dst_interface_name,
                       num_packets, packets_per_sec):
        """Add a UDPv6 stream from the source interface to the destination
           interface"""
        dbg_print('addUDPv6Stream({0} {1} {2} {3})'.format(src_interface_name,
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
        src_ip = self._getInterfaceIPv6Address(src_interface)
        dst_ip = self._getInterfaceIPv6Address(dst_interface)

        self._addUDPv6PacketStream(stream, src_mac, 0, 1, dst_mac,
                                   src_ip, dst_ip)
        self.drone.modifyStream(stream_cfg)

    def addUDPMacIncStream(self, src_interface_name, dst_interface_name,
                           src_mac, num_packets, packets_per_sec,
                           src_mac_count=0, src_mac_step=1):
        """Add a UDPv4 stream from the source interface to the
           destination interface, using the given src MAC addresses"""
        dbg_print('addUDPMacIncStream({0} {1} {2} {3} {4} {5} {6})'.
                  format(src_interface_name,
                         dst_interface_name,
                         src_mac,
                         src_mac_count,
                         src_mac_step,
                         num_packets,
                         packets_per_sec))
        src_interface = self._getInterfaceByName(src_interface_name)
        dst_interface = self._getInterfaceByName(dst_interface_name)
        stream_cfg = src_interface['stream_cfg']
        stream = self._addStream(stream_cfg, src_interface, num_packets,
                                 packets_per_sec)
        dst_mac = self._getInterfaceMacAddress(dst_interface)
        src_ip = self._getInterfaceIPv4Address(src_interface)
        dst_ip = self._getInterfaceIPv4Address(dst_interface)

        self._addUDPv4PacketStream(stream, src_mac, src_mac_count,
                                   src_mac_step, dst_mac, src_ip, dst_ip)
        self.drone.modifyStream(stream_cfg)

    def addUDPBroadcastStream(self, src_interface_name, num_packets,
                              packets_per_sec):
        """Add a UDPv4 broadcast stream from the source interface to the
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
        src_ip = self._getInterfaceIPv4Address(src_interface)
        dst_mac = 0xffffffffffff
        dst_ip = 0xc0a82aff
        self._addUDPv4PacketStream(stream, src_mac, 0, 1, dst_mac,
                                   src_ip, dst_ip)
        self.drone.modifyStream(stream_cfg)

    def addUDPMulticastStream(self, src_interface_name, group_str, num_packets,
                              packets_per_sec):
        """Add a UDPv4 multicast stream from the source interface to the
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
        src_ip = self._getInterfaceIPv4Address(src_interface)
        dst_ip = int(group)

        self._addUDPv4PacketStream(stream, src_mac, 0, 1, dst_mac,
                                   src_ip, dst_ip)
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
        src_ip = self._getInterfaceIPv4Address(src_interface)
        dst_ip = group

        self._addEthernetHeader(stream, src_mac=src_mac,
                                dst_mac=dst_mac)
        self._addEthertypeIPv4(stream)
        self._addIPv4Header(stream, src_ip=src_ip, dst_ip=dst_ip)
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
        self.drone.modifyPort(self.port_config)
        self.drone.clearStats(self.tx_port)
        self.drone.clearStats(self.rx_port)
        self.drone.clearStreamStats(self.guids)
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
        self.stream_stats = self.drone.getStreamStatsDict(self.guids)
        self._saveCaptures(test, method)
        self._cleanupRun()

        dbg_print('stream_stats: {0}'.format(self.stream_stats))

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
        stats = {
            'rx_pkts': 0,
            'tx_pkts': 0,
        }
        port_id = self._getInterfaceId(interface_name)
        if not self.stream_stats.port:
            return stats
        for port in self.stream_stats.port:
            dbg_print('port: {0}'.format(port))
            port_stream_stats = self.stream_stats.port[port]
            dbg_print('port_stream: {0}'.format(port_stream_stats))
            for squid in port_stream_stats.sguid:
                dbg_print('squid: {0}'.format(squid))
                dbg_print('squid {0}: {1}'.format(
                    squid, port_stream_stats.sguid[squid]))
                dbg_print('port_id: {0}'.format(
                    port_stream_stats.sguid[squid].port_id.id))
                if port_stream_stats.sguid[squid].port_id.id == port_id:
                    stats = {
                        'rx_pkts': port_stream_stats.total.rx_pkts,
                        'tx_pkts': port_stream_stats.total.tx_pkts,
                    }
                    return stats
        dbg_print('Not stats for interface {0}'.format(interface_name))
        return stats


if __name__ == '__main__':
    try:
        TRAFFIC = Traffic()
        print TRAFFIC.getInterfaceNames()
        TRAFFIC.addInterface('eth10')
        TRAFFIC.addInterface('eth11')
        TRAFFIC.addInterface('eth12')
        TRAFFIC.addInterface('eth13')
        TRAFFIC.addInterface('eth14')
        TRAFFIC.addInterface('eth15')
        TRAFFIC.addInterface('eth16')
        TRAFFIC.addInterface('eth17')
        TRAFFIC.learning()
        print TRAFFIC.getStats('eth10')
        print TRAFFIC.getStats('eth11')
        TRAFFIC.addUDPStream('eth10', 'eth11', 100, 10)
        TRAFFIC.addUDPStream('eth11', 'eth10', 50, 5)
        TRAFFIC.run()
        print 'Statistics for eth10: {0}'.format(TRAFFIC.getStats('eth10'))
        print 'Statistics for eth11: {0}'.format(TRAFFIC.getStats('eth11'))
    except KeyboardInterrupt:
        sys.exit(1)
