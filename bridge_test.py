#!/usr/bin/env python
"""Test the operation of a bridge on the SUT"""

import params
import sut
import time
import traffic
import unittest2
import xmlrunner


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

tx_5_stats = {
    'rx_pkts': 0L,
    'rx_bytes': 0L,
    'rx_pps': 0L,
    'rx_bps': 0L,
    'tx_pkts': 5L,
    'tx_bytes': 320L,
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

tx_40_stats = {
    'rx_pkts': 0L,
    'rx_bytes': 0L,
    'rx_pps': 0L,
    'rx_bps': 0L,
    'tx_pkts': 40L,
    'tx_bytes': 2560L,
    'tx_pps': 0L,
    'tx_bps': 0L,
    'rx_drops': 0L,
    'rx_errors': 0L,
    'rx_fifo_errors': 0L,
    'rx_frame_errors': 0L,
    }

rx_10_stats = {
    'rx_pkts': 10L,
    'rx_bytes': 640L,
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


class bridge_test(unittest2.TestCase):
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
        self.sut.up(self.config.SUT_LAN4)
        self.sut.up(self.config.SUT_LAN5)
        self.sut.up(self.config.SUT_LAN6)
        self.sut.up(self.config.SUT_LAN7)
        self.sut.up(self.config.SUT_LAN8)
        self.sut.up(self.config.SUT_OPTICAL3)
        self.sut.up(self.config.SUT_OPTICAL3)

        self.sut.addBridge('br1')
        self.sut.up('br1')
        self.sut.addBridgeInterface('br1', self.config.SUT_LAN1)
        self.sut.addBridgeInterface('br1', self.config.SUT_LAN2)
        self.sut.addBridgeInterface('br1', self.config.SUT_LAN3)
        self.sut.addBridgeInterface('br1', self.config.SUT_LAN4)
        self.sut.addBridgeInterface('br1', self.config.SUT_LAN6)

        # Wait the forwarding delay of the bridge
        time.sleep(10)

        self.traffic.addInterface(self.config.HOST_LAN0)
        self.traffic.addInterface(self.config.HOST_LAN1)
        self.traffic.addInterface(self.config.HOST_LAN2)
        self.traffic.addInterface(self.config.HOST_LAN3)
        self.traffic.addInterface(self.config.HOST_LAN4)
        self.traffic.addInterface(self.config.HOST_LAN5)
        self.traffic.addInterface(self.config.HOST_LAN6)
        self.traffic.addInterface(self.config.HOST_OPTICAL3)

    def test_01_learn(self):
        """Send learning packets, so the bridge knows which MAC address
           is where"""
        self.traffic.learning()

    def test_02_not_bridged(self):
        """lan0, lan5, and optical3 are not a member of a bridge. Send
           traffic on these ports, and make sure there is no traffic
           sent out other ports"""
        self.traffic.addUDPStream(self.config.HOST_LAN5,
                                  self.config.HOST_LAN0, 5, 5)
        self.traffic.addUDPStream(self.config.HOST_OPTICAL3,
                                  self.config.HOST_LAN0, 5, 5)
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN0, 5, 5)
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN5, 5, 5)
        self.traffic.addUDPBroadcastStream(self.config.HOST_OPTICAL3, 5, 5)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, tx_5_stats)
        self.assertEqual(stats_lan1, zero_stats)
        self.assertEqual(stats_lan2, zero_stats)
        self.assertEqual(stats_lan3, zero_stats)
        self.assertEqual(stats_lan4, zero_stats)
        self.assertEqual(stats_lan5, tx_10_stats)
        self.assertEqual(stats_lan6, zero_stats)
        self.assertEqual(stats_optical3, tx_10_stats)

    def test_03_bridged_unicast_lan1(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan1 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN1,
                                  self.config.HOST_LAN2, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN1,
                                  self.config.HOST_LAN3, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN1,
                                  self.config.HOST_LAN4, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN1,
                                  self.config.HOST_LAN6, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, tx_40_stats)

        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, rx_10_stats)
        self.assertEqual(stats_lan4, rx_10_stats)
        self.assertEqual(stats_lan5, zero_stats)
        self.assertEqual(stats_lan6, rx_10_stats)
        self.assertEqual(stats_optical3, zero_stats)

    def test_04_bridged_unicast_lan2(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan2 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN2,
                                  self.config.HOST_LAN1, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN2,
                                  self.config.HOST_LAN3, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN2,
                                  self.config.HOST_LAN4, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN2,
                                  self.config.HOST_LAN6, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, tx_40_stats)
        self.assertEqual(stats_lan3, rx_10_stats)
        self.assertEqual(stats_lan4, rx_10_stats)
        self.assertEqual(stats_lan5, zero_stats)
        self.assertEqual(stats_lan6, rx_10_stats)
        self.assertEqual(stats_optical3, zero_stats)

    def test_05_bridged_unicast_lan3(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan3 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN3,
                                  self.config.HOST_LAN1, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN3,
                                  self.config.HOST_LAN2, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN3,
                                  self.config.HOST_LAN4, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN3,
                                  self.config.HOST_LAN6, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, tx_40_stats)
        self.assertEqual(stats_lan4, rx_10_stats)
        self.assertEqual(stats_lan5, zero_stats)
        self.assertEqual(stats_lan6, rx_10_stats)
        self.assertEqual(stats_optical3, zero_stats)

    def test_06_bridged_unicast_lan4(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan4 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN4,
                                  self.config.HOST_LAN1, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN4,
                                  self.config.HOST_LAN2, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN4,
                                  self.config.HOST_LAN3, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN4,
                                  self.config.HOST_LAN6, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, rx_10_stats)
        self.assertEqual(stats_lan4, tx_40_stats)
        self.assertEqual(stats_lan5, zero_stats)
        self.assertEqual(stats_lan6, rx_10_stats)
        self.assertEqual(stats_optical3, zero_stats)

    def test_07_bridged_unicast_lan6(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan6 is the source"""
        self.traffic.addUDPStream(self.config.HOST_LAN6,
                                  self.config.HOST_LAN1, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN6,
                                  self.config.HOST_LAN2, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN6,
                                  self.config.HOST_LAN3, 10, 10)
        self.traffic.addUDPStream(self.config.HOST_LAN6,
                                  self.config.HOST_LAN4, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, zero_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, rx_10_stats)
        self.assertEqual(stats_lan4, rx_10_stats)
        self.assertEqual(stats_lan5, zero_stats)
        self.assertEqual(stats_lan6, tx_40_stats)
        self.assertEqual(stats_optical3, zero_stats)

    @unittest2.skip("skipping")
    def test_08_bridged_broadcast_lan0(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan0 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN0, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, tx_10_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, rx_10_stats)
        self.assertEqual(stats_lan4, zero_stats)
        self.assertEqual(stats_lan5, rx_10_stats)
        self.assertEqual(stats_lan6, zero_stats)
        self.assertEqual(stats_optical3, zero_stats)

    @unittest2.skip("skipping")
    def test_09_bridged_broadcast_lan1(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan1 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN1, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, rx_10_stats)
        self.assertEqual(stats_lan1, tx_10_stats)
        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, rx_10_stats)
        self.assertEqual(stats_lan4, zero_stats)
        self.assertEqual(stats_lan5, rx_10_stats)
        self.assertEqual(stats_lan6, zero_stats)
        self.assertEqual(stats_optical3, zero_stats)

    @unittest2.skip("skipping")
    def test_10_bridged_broadcast_lan2(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan2 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN2, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, rx_10_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, tx_10_stats)
        self.assertEqual(stats_lan3, rx_10_stats)
        self.assertEqual(stats_lan4, zero_stats)
        self.assertEqual(stats_lan5, rx_10_stats)
        self.assertEqual(stats_lan6, zero_stats)
        self.assertEqual(stats_optical3, zero_stats)

    @unittest2.skip("skipping")
    def test_11_bridged_broadcast_lan3(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan3 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN3, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, rx_10_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, tx_10_stats)
        self.assertEqual(stats_lan4, zero_stats)
        self.assertEqual(stats_lan5, rx_10_stats)
        self.assertEqual(stats_lan6, zero_stats)
        self.assertEqual(stats_optical3, zero_stats)

    @unittest2.skip("skipping")
    def test_12_bridged_broadcast_lan5(self):
        """Send traffic between bridged ports, and ensure they come out the
           expected ports. lan5 is the source of broadcast packets"""
        self.traffic.addUDPBroadcastStream(self.config.HOST_LAN5, 10, 10)
        self.traffic.run()

        stats_lan0 = self.traffic.getStats(self.config.HOST_LAN0)
        stats_lan1 = self.traffic.getStats(self.config.HOST_LAN1)
        stats_lan2 = self.traffic.getStats(self.config.HOST_LAN2)
        stats_lan3 = self.traffic.getStats(self.config.HOST_LAN3)
        stats_lan4 = self.traffic.getStats(self.config.HOST_LAN4)
        stats_lan5 = self.traffic.getStats(self.config.HOST_LAN5)
        stats_lan6 = self.traffic.getStats(self.config.HOST_LAN6)
        stats_optical3 = self.traffic.getStats(self.config.HOST_OPTICAL3)

        self.assertEqual(stats_lan0, rx_10_stats)
        self.assertEqual(stats_lan1, rx_10_stats)
        self.assertEqual(stats_lan2, rx_10_stats)
        self.assertEqual(stats_lan3, tx_10_stats)
        self.assertEqual(stats_lan4, zero_stats)
        self.assertEqual(stats_lan5, rx_10_stats)
        self.assertEqual(stats_lan6, zero_stats)
        self.assertEqual(stats_optical3, zero_stats)

    @unittest2.skip("skipping")
    def test_99_delete_bridge(self):
        """Destroy the bridge"""
        self.sut.deleteBridgeInterface('br1', self.config.SUT_LAN1)
        self.sut.deleteBridgeInterface('br1', self.config.SUT_LAN2)
        self.sut.deleteBridgeInterface('br1', self.config.SUT_LAN3)
        self.sut.deleteBridgeInterface('br1', self.config.SUT_LAN4)
        self.sut.deleteBridgeInterface('br1', self.config.SUT_LAN6)
        self.sut.deleteBridge('br1')

        # Ensure all the interfaces are down
        self.sut.down(self.config.SUT_LAN1)
        self.sut.down(self.config.SUT_LAN2)
        self.sut.down(self.config.SUT_LAN3)
        self.sut.down(self.config.SUT_LAN4)
        self.sut.down(self.config.SUT_LAN5)
        self.sut.down(self.config.SUT_LAN6)
        self.sut.down(self.config.SUT_LAN7)
        self.sut.down(self.config.SUT_LAN8)
        self.sut.down(self.config.OPTICAL3)
        self.sut.down(self.config.OPTICAL4)


if __name__ == '__main__':
    args = params.params()
    CONFIG = params.readConfig(args.config)
    SUT = sut.SUT(hostname=CONFIG.hostname, key=CONFIG.key)
    SUT.cleanSystem()
    TRAFFIC = traffic.Traffic()

    if args.xml:
        testRunner = unittest.TextTestRunner
    else:
        testRunner = xmlrunner.XMLTestRunner(output='test-reports')

    unittest2.main(failfast=args.failfast, verbosity=args.verbose,
                   buffer=False,
                   testRunner=testRunner)
