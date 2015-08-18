#!/usr/bin/env python
"""Model the System Under Test"""
import paramiko
import re

DEBUG = False


def dbg_print(args):
    """Print debug messages if they are enabled"""
    if DEBUG:
        print args


class SUT(object):
    """Class representing the System Under Test"""

    def __init__(self, hostname, key):
        self.sshClient = paramiko.SSHClient()
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshClient.connect(hostname, username='root', key_filename=key)
        self.exit_code = None
        self.error = ""
        self.interfaces = self.getInterfaces()

    def ssh(self, command):
        """Execute a command on the SUT, using SSH"""
        self.exit_code = None
        pattern = re.compile('exit code ([a-z0-9]+)')
        stdin, stdout, stderr = self.sshClient.exec_command(
            command + '; echo exit code $? ; exit\n')
        results = stdout.read()
        self.error = stderr.read()
        dbg_print(results)
        match = pattern.search(results)
        if match:
            self.exit_code = int(match.group(1))
        return results

    def checkExitCode(self, code):
        """Check the exit code is the expected value"""
        if self.exit_code != code:
            raise NameError('Exit code mismatch {0} != {1}\n{2}'.format(
                self.exit_code, code, self.error))

    def getInterfaces(self):
        """Return a list of network interface names"""
        interfaces = []
        results = self.ssh('ip link show')
        pattern = re.compile('[0-9]+: ([a-z0-9]+)')
        for line in results.splitlines():
            match = pattern.match(line)
            if match:
                interfaces.append(match.group(1))
        self.interfaces = interfaces
        self.checkExitCode(0)
        return interfaces

    def getBridges(self):
        """Return a list of bridge interface names"""
        bridges = []
        interfaces = self.getInterfaces()
        for interface in interfaces:
            if interface.startswith('br'):
                bridges.append(interface)
        return bridges

    def getBonds(self):
        """Return a list of bond interface names"""
        bonds = []
        interfaces = self.getInterfaces()
        for interface in interfaces:
            if interface.startswith('bond'):
                bonds.append(interface)
        return bonds

    def up(self, interface):
        """Set an interface up"""
        if interface not in self.interfaces:
            raise NameError('Up called for unknown interface')
        result = self.ssh('ip link set {0} up'.format(interface))
        if 'RTNETLINK answers' in result:
            raise NameError('Up failed')
        if 'Cannot find device' in result:
            raise NameError('Up failed, no such device')
        self.checkExitCode(0)

    def down(self, interface):
        """Set an interface down"""
        if interface not in self.interfaces:
            raise NameError('Down called for unknown interface')
        result = self.ssh('ip link set {0} down'.format(interface))
        if 'RTNETLINK answers' in result:
            raise NameError('Down failed')
        if 'Cannot find device' in result:
            raise NameError('Down failed, no such device')
        self.checkExitCode(0)

    def addAddress(self, interface, address):
        """Add an address to an interface"""
        if interface not in self.interfaces:
            raise NameError('addAddress called for unknown interface')
        self.ssh('ip addr add {0} dev {1}'.format(
            address, interface))
        self.checkExitCode(0)

    def delAddress(self, interface, address):
        """Delete an address from an interface"""
        if interface not in self.interfaces:
            raise NameError('addAddress called for unknown interface')
        self.ssh('ip addr del {0} dev {1}'.format(
            address, interface))
        self.checkExitCode(0)

    def flushAddresses(self, interface):
        """Remove all addresses from an interface"""
        if interface not in self.interfaces:
            raise NameError('flushAddresses called for unknown interface')
        self.ssh('ip addr flush dev {0}'.format(interface))
        self.checkExitCode(0)

    def deleteBridge(self, bridge):
        """Destroy the given bridge"""
        if bridge not in self.interfaces:
            raise NameError('deleteBridge called for unknown interface')
        if bridge not in self.getBridges():
            raise NameError('deleteBridge called for unknown bridge')
        self.down(bridge)
        self.ssh('brctl delbr {0}'.format(bridge))
        self.getInterfaces()
        self.checkExitCode(0)

    def addBridge(self, bridge):
        """Create the given bridge. Set the forwarding delay to 1 second, so
           we don't have to wait too long before the bridge starts
           forwaring packets"""
        if bridge in self.interfaces:
            raise NameError('addBridge called for known interface')
        if bridge in self.getBridges():
            raise NameError('addBridge called for known bridge')
        self.ssh('brctl addbr {0}'.format(bridge))
        self.getInterfaces()
        self.checkExitCode(0)
        self.ssh('brctl setfd {0} 2'.format(bridge))
        self.checkExitCode(0)

    def addBridgeInterface(self, bridge, interface):
        """Add an interface to a bridge"""
        if bridge not in self.interfaces:
            raise NameError('addBridgeInterface called for unknown bridge')
        if bridge not in self.getBridges():
            raise NameError('addBridgeInterface called for unknown bridge')
        if interface not in self.interfaces:
            raise NameError('addBridgeInterface called for unknown interface')
        self.ssh('brctl addif {0} {1}'.format(bridge, interface))
        self.checkExitCode(0)

    def deleteBridgeInterface(self, bridge, interface):
        """Deleye an interface from a bridge"""
        if bridge not in self.interfaces:
            raise NameError('deleteBridgeInterface called for unknown bridge')
        if bridge not in self.getBridges():
            raise NameError('deleteBridgeInterface called for unknown bridge')
        if interface not in self.interfaces:
            raise NameError(
                'deleteBridgeInterface called for unknown interface')
        self.ssh('brctl delif {0} {1}'.format(bridge, interface))
        self.checkExitCode(0)

    def cleanSystem(self):
        """Clean the system i.e. remove all bridges, check there are no bonds,
           put all interfaces down"""
        bonds = self.getBonds()
        bridges = self.getBridges()
        interfaces = self.getInterfaces()
        interfaces = [interface for interface in interfaces if
                      interface.startswith('lan') or
                      interface.startswith('optical')]
        if len(bonds):
            #  Todo: Implement cleanup of bonds
            raise NameError('SUT has some bonds: {0}'.format(bonds))
        for bridge in bridges:
            self.deleteBridge(bridge)
        for interface in interfaces:
            self.flushAddresses(interface)
            self.down(interface)
