#!/usr/bin/env python3

import amulet
import unittest


class TestDeploy(unittest.TestCase):
    """
    Trivial deployment test for Apache Flume HDFS.

    This charm cannot do anything useful by itself, so integration testing
    is done in the bundle.
    """
    def test_deploy(self):
        self.d = amulet.Deployment(series='xenial')
        self.d.add('flume-hdfs', 'cs:~bigdata-dev/xenial/apache-flume-hdfs')
        self.d.setup(timeout=900)
        self.d.sentry.wait(timeout=1800)
        self.unit = self.d.sentry['flume-hdfs'][0]


if __name__ == '__main__':
    unittest.main()
