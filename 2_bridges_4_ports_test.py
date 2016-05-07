#!/usr/bin/env python
"""Test the operation of two bridges on the SUT"""

import time
import unittest2
import xmlrunner

import params
import sut
import traffic


zero_stats = {
    'rx_pkts': 0L,
    'rx_bytes': 0L,
    'rx_pps': 0L,
    'rx_bps': 0L,
    'tx_pkts': 0L,
    'tx_bytes': 0L,
    'tx_pps': 0L,
    'tx_bps': 0L,
    'rx_drops': 0L,
    'rx_errors': 0L,
    'rx_fifo_errors': 0L,
    'rx_frame_errors': 0L,
    }

tx_10_stats = {
    'rx_pkts': 0L,
    'rx_bytes': 0L,
    'rx_pps': 0L,
    'rx_bps': 0L,
    'tx_pkts': 10L,
    'tx_bytes': 640L,
    'tx_pps': 0L,
    'tx_bps': 0L,
    'rx_drops': 0L,
    'rx_errors': 0L,
    'rx_fifo_errors': 0L,
    'rx_frame_errors': 0L,
    }

tx_30_stats = {
    'rx_pkts': 0L,
    'rx_bytes': 0L,
    'rx_pps': 0L,
    'rx_bps': 0L,
    'tx_pkts': 30L,
    'tx_bytes': 1920L,
    'tx_pps': 0L,
    'tx_bps': 0L,
    'rx_drops': 0L,
    'rx_errors': 0L,
    'rx_fifo_errors': 0L,
    'rx_frame_errors': 0L,
    }

rx_10_stats = {
    'rx_pkts': 10L,
    'rx_bytes': 460L,
    'rx_pps': 0L,
    'rx_bps': 0L,
    'tx_pkts': 0L,
    'tx_bytes': 0L,
    'tx_pps': 0L,
    'tx_bps': 0L,
    'rx_drops': 0L,
    'rx_errors': 0L,
    'rx_fifo_errors': 0L,
    'rx_frame_errors': 0L,
    }

rx_30_stats = {
    'rx_pkts': 30L,
    'rx_bytes': 1380L,
    'rx_pps': 0L,
    'rx_bps': 0L,
    'tx_pkts': 0L,
    'tx_bytes': 0L,
    'tx_pps': 0L,
    'tx_bps': 0L,
    'rx_drops': 0L,
    'rx_errors': 0L,
    'rx_fifo_errors': 0L,
    'rx_frame_errors': 0L,
    }

SUT = None
TRAFFIC = None
CONFIG = None


class two_bridges_4_ports_test(unittest2.TestCase):
    '''Class containing the test cases'''

    def setUp(self):
        """Setup ready to perform the test"""
        self.sut = SUT
        self.traffic = TRAFFIC
        self.config = CONFIG
        self.maxDiff = None

    def test_01_create_bridge(self):
        """Create the bridge"""
        # Ensure all the interfaces are up
        self.sut.up(self.config.SUT_MASTER)
        self.sut.up(self.config.SUT_LAN0)
        self.sut.up(self.config.SUT_LAN1)
        self.sut.up(self.config.SUT_LAN2)
        self.sut.up(self.config.SUT_LAN3)

        self.sut.addBridge('br1')
        self.sut.up('br1')
        self.sut.addBridgeInterface('br1', self.config.SUT_LAN0)
        self.sut.addBridgeInterface('br1', self.config.SUT_LAN1)

        self.sut.addBridge('br2')
        self.sut.up('br2')
        self.sut.addBridgeInterface('br2', self.config.SUT_LAN2)
        self.sut.addBridgeInterface('br2', self.config.SUT_LAN3)

        # Wait the forwarding delay of the bridge
        time.sleep(10)

        self.traffic.addInterface(self.config.HOST_LAN0)
        self.traffic.addInterface(self.config.HOST_LAN1)
        self.traffic.addInterface(self.config.HOST_LAN2)
        self.traffic.addInterface(self.config.HOST_LAN3)

    def test_01_learn(self):
        """Send learning packets, so the bridge knows which MAC address
           is where"""
        self.traffic.learning()

    def test_02_bridged_unicast_lan0(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan0 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN0,
                                  self.config.HOST_LAN1, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN0,
                                  self.config.HOST_LAN2, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN0,
                                  self.config.HOST_LAN3, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)

        self.assertEqual(stats_lan0, tx_30_stats)
        # Not obviouus: The destination MAC for LAN2 and LAN3 are not
        # known, so the packets are flooded out LAN 1 as weel.
        self.assertEqual(stats_lan1, rx_30_stats)
        self.assertEqual(stats_lan2, zero_stats)
        self.assertEqual(stats_lan3, zero_stats)

    def test_03_bridged_unicast_lan1(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan1 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN1,
                                  self.config.HOST_LAN0, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN1,
                                  self.config.HOST_LAN2, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN1,
                                  self.config.HOST_LAN3, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)

        self.assertEqual(stats_lan0, rx_30_stats)
        self.assertEqual(stats_lan1, tx_30_stats)
        self.assertEqual(stats_lan2, zero_stats)
        self.assertEqual(stats_lan3, zero_stats)

    def test_04_bridged_unicast_lan2(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan2 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN2,
                                  self.config.HOST_LAN0, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN2,
                                  self.config.HOST_LAN1, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN2,
                                  self.config.HOST_LAN3, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, zero_stats)
        self.assertEqual(stats_lan2, tx_30_stats)
        self.assertEqual(stats_lan3, rx_30_stats)

    def test_05_bridged_unicast_lan3(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan3 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN3,
                                  self.config.HOST_LAN0, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN3,
                                  self.config.HOST_LAN1, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN3,
                                  self.config.HOST_LAN2, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, zero_stats)
        self.assertEqual(stats_lan2, rx_30_stats)
        self.assertEqual(stats_lan3, tx_30_stats)

    def test_06_bridged_broadcast_lan0(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan0 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN0, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)

        self.assertEqual(stats_lan0, tx_10_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, zero_stats)
        self.assertEqual(stats_lan3, zero_stats)

    def test_07_bridged_broadcast_lan1(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan1 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN1, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)

        self.assertEqual(stats_lan0, rx_10_stats)
        self.assertEqual(stats_lan1, tx_10_stats)
        self.assertEqual(stats_lan2, zero_stats)
        self.assertEqual(stats_lan3, zero_stats)

    def test_08_bridged_broadcast_lan2(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan2 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN2, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, zero_stats)
        self.assertEqual(stats_lan2, tx_10_stats)
        self.assertEqual(stats_lan3, rx_10_stats)

    def test_09_bridged_broadcast_lan3(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan3 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN3, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, zero_stats)
        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, tx_10_stats)

    def test_99_delete_bridge(self):
        """Destroy the bridge"""
        self.sut.deleteBridgeInterface('br1', self.config.SUT_LAN0)
        self.sut.deleteBridgeInterface('br1', self.config.SUT_LAN1)
        self.sut.deleteBridgeInterface('br2', self.config.SUT_LAN2)
        self.sut.deleteBridgeInterface('br2', self.config.SUT_LAN3)
        self.sut.deleteBridge('br1')
        self.sut.deleteBridge('br2')

        # Ensure all the interfaces are down
        self.sut.down(self.config.SUT_LAN0)
        self.sut.down(self.config.SUT_LAN1)
        self.sut.down(self.config.SUT_LAN2)
        self.sut.down(self.config.SUT_LAN3)


if __name__ == '__main__':
    args = params.params()
    CONFIG = params.readConfig(args.config)
    SUT = sut.SUT(hostname=CONFIG.hostname, key=CONFIG.key)
    SUT.cleanSystem()
    TRAFFIC = traffic.Traffic()

    if args.xml:
        testRunner = xmlrunner.XMLTestRunner(output='test-reports',
                                             verbosity=args.verbose)
    else:
        testRunner = unittest2.TextTestRunner(failfast=args.failfast,
                                              verbosity=args.verbose)

    unittest2.main(buffer=False, testRunner=testRunner, exit=False)
