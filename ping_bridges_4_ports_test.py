#!/usr/bin/env python
"""Ping bridges interfaces on the SUT. Each bridge has a single
   interface as member and the IP address that would normally be on
   the interface is placed on the bridge."""

import host
import params
import sut
import sys
import time
import unittest2
import xmlrunner


SUT = None
HOST = None
CONFIG = None


class ping_bridges_4_ports_test(unittest2.TestCase):
    '''Class containing the test cases'''

    def setUp(self):
        """Setup ready to perform the test"""
        self.sut = SUT
        self.host = HOST
        self.config = CONFIG
        self.maxDiff = None

    def test_00_setup_sut(self):
        """Setup IP addresses on the SUT interfaces"""
        # Ensure all the interfaces are up
        self.sut.up(self.config.SUT_MASTER)
        self.sut.up(self.config.SUT_LAN0)
        self.sut.up(self.config.SUT_LAN1)
        self.sut.up(self.config.SUT_LAN2)
        self.sut.up(self.config.SUT_LAN3)

        self.sut.addAddress(self.config.SUT_LAN0, '192.168.10.2/24')
        self.sut.addAddress(self.config.SUT_LAN1, '192.168.11.2/24')
        self.sut.addAddress(self.config.SUT_LAN2, '192.168.12.2/24')
        self.sut.addAddress(self.config.SUT_LAN3, '192.168.13.2/24')

        # Allow time for the interfaces to come up
        time.sleep(10)

    def test_01_setup_host(self):
        """Setup IP addresses on the host device"""
        self.host.addInterface(self.config.HOST_LAN0)
        self.host.addInterface(self.config.HOST_LAN1)
        self.host.addInterface(self.config.HOST_LAN2)
        self.host.addInterface(self.config.HOST_LAN3)

        self.host.cleanSystem()

        self.host.up(self.config.HOST_LAN0)
        self.host.up(self.config.HOST_LAN1)
        self.host.up(self.config.HOST_LAN2)
        self.host.up(self.config.HOST_LAN3)

        self.host.addAddress(self.config.HOST_LAN0, '192.168.10.1/24')
        self.host.addAddress(self.config.HOST_LAN1, '192.168.11.1/24')
        self.host.addAddress(self.config.HOST_LAN2, '192.168.12.1/24')
        self.host.addAddress(self.config.HOST_LAN3, '192.168.13.1/24')

    def test_02_ping(self):
        """Ping the SUT. We expect replies for all interfaces"""
        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_03_lan0_br0(self):
        """Create a bridge and place only lan0 in it. Move lan0
           IP address to the bridge"""
        self.sut.delAddress(self.config.SUT_LAN0, '192.168.10.2/24')
        self.sut.addBridge('br0')
        self.sut.up('br0')
        self.sut.addBridgeInterface('br0', self.config.SUT_LAN0)
        self.sut.addAddress('br0', '192.168.10.2/24')

        # Wait the forwarding delay of the bridge
        time.sleep(7)

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_04_lan2_br2(self):
        """Create a bridge and place only lan2 in it. Move lan2
           IP address to the bridge"""
        self.sut.delAddress(self.config.SUT_LAN2, '192.168.12.2/24')
        self.sut.addBridge('br2')
        self.sut.up('br2')
        self.sut.addBridgeInterface('br2', self.config.SUT_LAN2)
        self.sut.addAddress('br2', '192.168.12.2/24')

        # Wait the forwarding delay of the bridge
        time.sleep(5)

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_05_lan3_br3(self):
        """Create a bridge and place only lan3 in it. Move lan3
           IP address to the bridge"""
        self.sut.delAddress(self.config.SUT_LAN3, '192.168.13.2/24')
        self.sut.addBridge('br3')
        self.sut.up('br3')
        self.sut.addBridgeInterface('br3', self.config.SUT_LAN3)
        self.sut.addAddress('br3', '192.168.13.2/24')

        # Wait the forwarding delay of the bridge
        time.sleep(5)

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_06_lan1_br1(self):
        """Create a bridge and place only lan1 in it. Move lan1
           IP address to the bridge"""
        self.sut.delAddress(self.config.SUT_LAN1, '192.168.11.2/24')
        self.sut.addBridge('br1')
        self.sut.up('br1')
        self.sut.addBridgeInterface('br1', self.config.SUT_LAN1)
        self.sut.addAddress('br1', '192.168.11.2/24')

        # Wait the forwarding delay of the bridge
        time.sleep(5)

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_07_remove_br0(self):
        """Remove br0 and place the IP address back on lan0"""
        self.sut.down('br0')
        self.sut.deleteBridge('br0')
        self.sut.addAddress(self.config.SUT_LAN0, '192.168.10.2/24')

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_08_remove_br2(self):
        """Remove br2 and place the IP address back on lan2"""
        self.sut.down('br2')
        self.sut.deleteBridge('br2')
        self.sut.addAddress(self.config.SUT_LAN2, '192.168.12.2/24')

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_09_remove_br3(self):
        """Remove br3 and place the IP address back on lan3"""
        self.sut.down('br3')
        self.sut.deleteBridge('br3')
        self.sut.addAddress(self.config.SUT_LAN3, '192.168.13.2/24')

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_09_remove_br1(self):
        """Remove br1 and place the IP address back on lan1"""
        self.sut.down('br1')
        self.sut.deleteBridge('br1')
        self.sut.addAddress(self.config.SUT_LAN1, '192.168.11.2/24')

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))

    def test_99_ping_down(self):
        """Down the interfaces on the SUT and then ping the SUT.
           We don't expect replies from any interfaces"""
        self.sut.down(self.config.SUT_LAN0)
        self.sut.down(self.config.SUT_LAN1)
        self.sut.down(self.config.SUT_LAN2)
        self.sut.down(self.config.SUT_LAN3)

        self.assertFalse(self.host.ping('192.168.10.2'))
        self.assertFalse(self.host.ping('192.168.11.2'))
        self.assertFalse(self.host.ping('192.168.12.2'))
        self.assertFalse(self.host.ping('192.168.13.2'))

if __name__ == '__main__':
    args = params.params()
    CONFIG = params.readConfig(args.config)
    SUT = sut.SUT(hostname=CONFIG.hostname, key=CONFIG.key)
    SUT.cleanSystem()
    HOST = host.HOST()

    if args.xml:
        testRunner = xmlrunner.XMLTestRunner(output='test-reports', verbosity=args.verbose)
    else:
        testRunner = unittest2.TextTestRunner(failfast=args.failfast, verbosity=args.verbose)

    unittest2.main(buffer=False, testRunner=testRunner, exit=False)
    HOST.cleanSystem()
