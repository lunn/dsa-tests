#!/usr/bin/env python
"""Ping bridges interfaces on the SUT. Each bridge has a single
   interface as member and the IP address that would normally be on
   the interface is placed on the bridge."""

import host
import params
import sut
import time
import unittest2


SUT = None
HOST = None
CONFIG = None


class ping_individual_test(unittest2.TestCase):
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
        self.sut.up(self.config.SUT_LAN4)
        self.sut.up(self.config.SUT_LAN5)
        self.sut.up(self.config.SUT_LAN6)
        self.sut.up(self.config.SUT_LAN7)
        self.sut.up(self.config.SUT_LAN8)
        self.sut.up(self.config.SUT_OPTICAL3)
        self.sut.up(self.config.SUT_OPTICAL4)

        self.sut.addAddress(self.config.SUT_LAN0, '192.168.10.2/24')
        self.sut.addAddress(self.config.SUT_LAN1, '192.168.11.2/24')
        self.sut.addAddress(self.config.SUT_LAN2, '192.168.12.2/24')
        self.sut.addAddress(self.config.SUT_LAN3, '192.168.13.2/24')
        self.sut.addAddress(self.config.SUT_LAN4, '192.168.14.2/24')
        self.sut.addAddress(self.config.SUT_LAN5, '192.168.15.2/24')
        self.sut.addAddress(self.config.SUT_LAN6, '192.168.16.2/24')
        self.sut.addAddress(self.config.SUT_OPTICAL3, '192.168.17.2/24')

        # Allow time for the interfaces to come up
        time.sleep(10)

    def test_01_setup_host(self):
        """Setup IP addresses on the host device"""
        self.host.addInterface(self.config.HOST_LAN0)
        self.host.addInterface(self.config.HOST_LAN1)
        self.host.addInterface(self.config.HOST_LAN2)
        self.host.addInterface(self.config.HOST_LAN3)
        self.host.addInterface(self.config.HOST_LAN4)
        self.host.addInterface(self.config.HOST_LAN5)
        self.host.addInterface(self.config.HOST_LAN6)
        self.host.addInterface(self.config.HOST_OPTICAL3)
        self.host.cleanSystem()

        self.host.up(self.config.HOST_LAN0)
        self.host.up(self.config.HOST_LAN1)
        self.host.up(self.config.HOST_LAN2)
        self.host.up(self.config.HOST_LAN3)
        self.host.up(self.config.HOST_LAN4)
        self.host.up(self.config.HOST_LAN5)
        self.host.up(self.config.HOST_LAN6)
        self.host.up(self.config.HOST_OPTICAL3)

        self.host.addAddress(self.config.HOST_LAN0, '192.168.10.1/24')
        self.host.addAddress(self.config.HOST_LAN1, '192.168.11.1/24')
        self.host.addAddress(self.config.HOST_LAN2, '192.168.12.1/24')
        self.host.addAddress(self.config.HOST_LAN3, '192.168.13.1/24')
        self.host.addAddress(self.config.HOST_LAN4, '192.168.14.1/24')
        self.host.addAddress(self.config.HOST_LAN5, '192.168.15.1/24')
        self.host.addAddress(self.config.HOST_LAN6, '192.168.16.1/24')
        self.host.addAddress(self.config.HOST_OPTICAL3, '192.168.17.1/24')

    def test_02_ping(self):
        """Ping the SUT. We expect replies for all interfaces"""
        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
    def test_03_lan0_br0(self):
        """Create a bridge and place only lan0 in it. Move lan0
           IP address to the bridge"""
        self.sut.delAddress(self.config.SUT_LAN0, '192.168.10.2/24')
        self.sut.addBridge('br0')
        self.sut.up('br0')
        self.sut.addBridgeInterface('br0', self.config.SUT_LAN0)
        self.sut.addAddress('br0', '192.168.10.2/24')

        # Wait the forwarding delay of the bridge
        time.sleep(5)

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
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
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
    def test_05_lan4_br4(self):
        """Create a bridge and place only lan4 in it. Move lan4
           IP address to the bridge"""
        self.sut.delAddress(self.config.SUT_LAN4, '192.168.14.2/24')
        self.sut.addBridge('br4')
        self.sut.up('br4')
        self.sut.addBridgeInterface('br4', self.config.SUT_LAN4)
        self.sut.addAddress('br4', '192.168.14.2/24')

        # Wait the forwarding delay of the bridge
        time.sleep(5)

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
    def test_06_lan6_br6(self):
        """Create a bridge and place only lan6 in it. Move lan6
           IP address to the bridge"""
        self.sut.delAddress(self.config.SUT_LAN6, '192.168.16.2/24')
        self.sut.addBridge('br6')
        self.sut.up('br6')
        self.sut.addBridgeInterface('br6', self.config.SUT_LAN6)
        self.sut.addAddress('br6', '192.168.16.2/24')

        # Wait the forwarding delay of the bridge
        time.sleep(5)

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
    def test_07_remove_br0(self):
        """Remove br0 and place the IP address back on lan0"""
        self.sut.down('br0')
        self.sut.deleteBridge('br0')
        self.sut.addAddress(self.config.SUT_LAN0, '192.168.10.2/24')

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
    def test_08_remove_br2(self):
        """Remove br2 and place the IP address back on lan2"""
        self.sut.down('br2')
        self.sut.deleteBridge('br2')
        self.sut.addAddress(self.config.SUT_LAN2, '192.168.12.2/24')

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
    def test_09_remove_br4(self):
        """Remove br4 and place the IP address back on lan4"""
        self.sut.down('br4')
        self.sut.deleteBridge('br4')
        self.sut.addAddress(self.config.SUT_LAN4, '192.168.14.2/24')

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
    def test_09_remove_br6(self):
        """Remove br6 and place the IP address back on lan6"""
        self.sut.down('br6')
        self.sut.deleteBridge('br6')
        self.sut.addAddress(self.config.SUT_LAN6, '192.168.16.2/24')

        self.assertTrue(self.host.ping('192.168.10.2'))
        self.assertTrue(self.host.ping('192.168.11.2'))
        self.assertTrue(self.host.ping('192.168.12.2'))
        self.assertTrue(self.host.ping('192.168.13.2'))
        self.assertTrue(self.host.ping('192.168.14.2'))
        self.assertTrue(self.host.ping('192.168.15.2'))
        self.assertTrue(self.host.ping('192.168.16.2'))
        self.assertTrue(self.host.ping('192.168.17.2'))

    @unittest2.skip("skipping")
    def test_99_ping_down(self):
        """Down the interfaces on the SUT and then ping the SUT.
           We don't expect replies from any interfaces"""
        self.sut.down(self.config.SUT_LAN0)
        self.sut.down(self.config.SUT_LAN1)
        self.sut.down(self.config.SUT_LAN2)
        self.sut.down(self.config.SUT_LAN3)
        self.sut.down(self.config.SUT_LAN4)
        self.sut.down(self.config.SUT_LAN5)
        self.sut.down(self.config.SUT_LAN6)
        self.sut.down(self.config.SUT_LAN7)
        self.sut.down(self.config.SUT_LAN8)
        self.sut.down(self.config.SUT_OPTICAL3)
        self.sut.down(self.config.SUT_OPTICAL4)

        self.assertFalse(self.host.ping('192.168.10.2'))
        self.assertFalse(self.host.ping('192.168.11.2'))
        self.assertFalse(self.host.ping('192.168.12.2'))
        self.assertFalse(self.host.ping('192.168.13.2'))
        self.assertFalse(self.host.ping('192.168.14.2'))
        self.assertFalse(self.host.ping('192.168.15.2'))
        self.assertFalse(self.host.ping('192.168.16.2'))
        self.assertFalse(self.host.ping('192.168.17.2'))

if __name__ == '__main__':
    args = params.params()
    CONFIG = params.readConfig(args.config)
    SUT = sut.SUT(hostname=CONFIG.hostname, key=CONFIG.key)
    SUT.cleanSystem()
    HOST = host.HOST()
    unittest2.main(failfast=args.failfast, verbosity=args.verbose,
                   buffer=False)
    HOST.cleanSystem()
