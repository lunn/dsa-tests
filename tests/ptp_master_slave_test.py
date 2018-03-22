#!/usr/bin/env python
"""Test PTP support."""

import datetime
import os
import time
import unittest2
import xmlrunner

import host
import params
import sut


SUT_MASTER = None
CONFIG_MASTER = None
SUT_SLAVE = None
CONFIG_SLAVE = None
HOST = None

class Ptp_master_slave_test(unittest2.TestCase):
    '''Class containing the test cases'''

    def setUp(self):
        """Setup ready to perform the test"""
        self.sut_master = SUT_MASTER
        self.config_master = CONFIG_MASTER
        self.sut_slave = SUT_SLAVE
        self.config_slave = CONFIG_SLAVE
        self.host = HOST
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.maxDiff = None

    def test_00_setup_master_ipv4(self):
        """Setup the interfaces on the PTP master, for UDP test"""

        # Ensure all the interfaces are up
        self.sut_master.up(self.config_master.SUT_MASTER)
        self.sut_master.up(self.config_master.SUT_LAN0)
        self.sut_master.addAddress(self.config_master.SUT_LAN0, '192.168.10.1/24')

        self.sut_master.serviceStop('ptp4l')
        self.sut_master.phcSet(self.config_master.SUT_LAN0, 0)

        self.sut_master.sftpPut(
            self.test_dir + '/ptp_master_slave_test/master-ipv4-ptp4l.conf',
            '/etc/ptp4l.conf')

        self.sut_master.serviceStart('ptp4l')

    def test_01_setup_slave_ipv4(self):
        """Setup the interfaces on the PTP slave, for UDP test"""

        # Ensure all the interfaces are up
        self.sut_slave.up(self.config_slave.SUT_MASTER)
        self.sut_slave.up(self.config_slave.SUT_LAN0)
        self.sut_slave.addAddress(self.config_slave.SUT_LAN0, '192.168.10.2/24')

        self.sut_slave.serviceStop('ptp4l')

        beginning = datetime.datetime(2018, 1, 1)
        seconds = time.mktime(beginning.timetuple())
        self.sut_slave.phcSet(self.config_slave.SUT_LAN0, seconds)
        phc_seconds, _ = self.sut_slave.phcGet(self.config_slave.SUT_LAN0)
        self.assertAlmostEqual(seconds, phc_seconds, places=0)

        self.sut_slave.sftpPut(
            self.test_dir + '/ptp_master_slave_test/slave-ipv4-ptp4l.conf',
            '/etc/ptp4l.conf')

        self.sut_slave.serviceStart('ptp4l')

    def test_02_check_slave_ipv4(self):
        """Check that the slave has a similar time to the master"""
        time.sleep(20)

        master_seconds, _ = self.sut_master.phcGet(self.config_master.SUT_LAN0)
        slave_seconds, _ = self.sut_slave.phcGet(self.config_slave.SUT_LAN0)

        self.assertAlmostEqual(master_seconds, slave_seconds, places=0)

    def test_03_setup_master_reversed_ipv4(self):
        """Setup the PTP master - reversed - UDP"""

        self.sut_slave.serviceStop('ptp4l')
        self.sut_slave.phcSet(self.config_slave.SUT_LAN0, 0)

        self.sut_slave.sftpPut(
            self.test_dir + '/ptp_master_slave_test/slave-ipv4-reversed-ptp4l.conf',
            '/etc/ptp4l.conf')

        self.sut_slave.serviceStart('ptp4l')

    def test_04_setup_slave_reversed_ipv4(self):
        """Setup the PTP slave - reversed - UDP"""

        self.sut_master.serviceStop('ptp4l')

        beginning = datetime.datetime(2018, 1, 1)
        seconds = time.mktime(beginning.timetuple())
        self.sut_master.phcSet(self.config_master.SUT_LAN0, seconds)
        phc_seconds, _ = self.sut_master.phcGet(self.config_master.SUT_LAN0)
        self.assertAlmostEqual(seconds, phc_seconds, places=0)

        self.sut_master.sftpPut(
            self.test_dir + '/ptp_master_slave_test/master-ipv4-reversed-ptp4l.conf',
            '/etc/ptp4l.conf')

        self.sut_master.serviceStart('ptp4l')

    def test_05_check_slave_reversed_ipv4(self):
        """Check that the slave has a similar time to the master"""
        time.sleep(20)

        master_seconds, _ = self.sut_master.phcGet(self.config_master.SUT_LAN0)
        slave_seconds, _ = self.sut_slave.phcGet(self.config_slave.SUT_LAN0)

        self.assertAlmostEqual(master_seconds, slave_seconds, places=0)

    def test_06_setup_master_l2(self):
        """Setup the interfaces on the PTP master, for L2 test"""

        self.sut_master.serviceStop('ptp4l')
        self.sut_master.phcSet(self.config_master.SUT_LAN0, 0)

        self.sut_master.sftpPut(
            self.test_dir + '/ptp_master_slave_test/master-l2-ptp4l.conf',
            '/etc/ptp4l.conf')

        self.sut_master.serviceStart('ptp4l')

    def test_07_setup_slave_l2(self):
        """Setup the interfaces on the PTP slave, for L2 test"""

        self.sut_slave.serviceStop('ptp4l')

        beginning = datetime.datetime(2018, 1, 1)
        seconds = time.mktime(beginning.timetuple())
        self.sut_slave.phcSet(self.config_slave.SUT_LAN0, seconds)
        phc_seconds, _ = self.sut_slave.phcGet(self.config_slave.SUT_LAN0)
        self.assertAlmostEqual(seconds, phc_seconds, places=0)

        self.sut_slave.sftpPut(
            self.test_dir + '/ptp_master_slave_test/slave-l2-ptp4l.conf',
            '/etc/ptp4l.conf')

        self.sut_slave.serviceStart('ptp4l')

    def test_08_check_slave_l2(self):
        """Check that the slave has a similar time to the master"""
        time.sleep(20)

        master_seconds, _ = self.sut_master.phcGet(self.config_master.SUT_LAN0)
        slave_seconds, _ = self.sut_slave.phcGet(self.config_slave.SUT_LAN0)

        self.assertAlmostEqual(master_seconds, slave_seconds, places=0)

    def test_09_setup_master_ipv6(self):
        """Setup the interfaces on the PTP master, for L2 test"""

        self.sut_master.serviceStop('ptp4l')
        self.sut_master.phcSet(self.config_master.SUT_LAN0, 0)

        self.sut_master.sftpPut(
            self.test_dir + '/ptp_master_slave_test/master-ipv6-ptp4l.conf',
            '/etc/ptp4l.conf')

        self.sut_master.serviceStart('ptp4l')

    def test_10_setup_slave_ipv6(self):
        """Setup the interfaces on the PTP slave, for L2 test"""

        self.sut_slave.serviceStop('ptp4l')

        beginning = datetime.datetime(2018, 1, 1)
        seconds = time.mktime(beginning.timetuple())
        self.sut_slave.phcSet(self.config_slave.SUT_LAN0, seconds)
        phc_seconds, _ = self.sut_slave.phcGet(self.config_slave.SUT_LAN0)
        self.assertAlmostEqual(seconds, phc_seconds, places=0)

        self.sut_slave.sftpPut(
            self.test_dir + '/ptp_master_slave_test/slave-ipv6-ptp4l.conf',
            '/etc/ptp4l.conf')

        self.sut_slave.serviceStart('ptp4l')

    def test_11_check_slave_ipv6(self):
        """Check that the slave has a similar time to the master"""
        time.sleep(20)

        master_seconds, _ = self.sut_master.phcGet(self.config_master.SUT_LAN0)
        slave_seconds, _ = self.sut_slave.phcGet(self.config_slave.SUT_LAN0)

        self.assertAlmostEqual(master_seconds, slave_seconds, places=0)

    def test_99_cleanup(self):
        """Stop the daemons"""
        self.sut_slave.serviceStop('ptp4l')
        self.sut_master.serviceStop('ptp4l')


if __name__ == '__main__':
    ARGS = params.params()
    CONFIG_SLAVE = params.readConfig(ARGS.config)
    SUT_SLAVE = sut.SUT(hostname=CONFIG_SLAVE.hostname,
                        key=CONFIG_SLAVE.key,
                        mgmt=CONFIG_SLAVE.SUT_MGMT)
    SUT_SLAVE.cleanSystem()

    CONFIG_MASTER = params.readConfig(ARGS.config_master)
    SUT_MASTER = sut.SUT(hostname=CONFIG_MASTER.hostname,
                         key=CONFIG_MASTER.key,
                         mgmt=CONFIG_MASTER.SUT_MGMT)

    SUT_MASTER.cleanSystem()
    HOST = host.HOST()

    if ARGS.xml:
        TEST_RUNNER = xmlrunner.XMLTestRunner(output='test-reports',
                                              verbosity=ARGS.verbose)
    else:
        TEST_RUNNER = unittest2.TextTestRunner(failfast=ARGS.failfast,
                                               verbosity=ARGS.verbose)

    unittest2.main(buffer=False, testRunner=TEST_RUNNER, exit=False)
    HOST.cleanSystem()
