Distributed Switch Architecture tests

Directory structure:

bin
===

Collection of shell scripts for building, controlling relays/power controls of
boards and running a tftpboot sequence.

board-configs
=============

Board configuration files describing both the host device running the tests and
the System Under Test.

docs
====

Documentation sources under LyX format.

jenkins-jobs
============

YAML files to trigger builds and tests using jenkins-build.

kernel-configs
==============

Kernel configuration fragments to build the kernel with for the different boards
support.

src
===

Sources for miscellaneous applications used for testing (e.g: relay status
display).

tests
=====

Python sources of the different tests being ran on the boards.
