#!/usr/bin/env python
"""Ping individual interfaces of SUT"""

import host
import params
import sut
import time
import unittest2
import xmlrunner


SUT = None
HOST = None
CONF = None


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
        time.sleep(5)

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

    def test_03_ping_down(self):
        """Down the interfaces on the SUT and then ping the SUT.
           We don't expect replies for all interfaces"""
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
    CONFIG = params.readConfig(args.config, fourPorts=False)
    SUT = sut.SUT(hostname=CONFIG.hostname, key=CONFIG.key)
    SUT.cleanSystem()
    HOST = host.HOST()

    if args.xml:
        testRunner = xmlrunner.XMLTestRunner(output='test-reports', verbosity=args.verbose)
    else:
        testRunner = unittest2.TextTestRunner(failfast=args.failfast, verbosity=args.verbose)

    unittest2.main(buffer=False, testRunner=testRunner, exit=False)
    HOST.cleanSystem()
