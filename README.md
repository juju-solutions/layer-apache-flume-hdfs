# Overview

Flume is a distributed, reliable, and available service for efficiently
collecting, aggregating, and moving large amounts of log data. It has a simple
and flexible architecture based on streaming data flows. It is robust and fault
tolerant with tunable reliability mechanisms and many failover and recovery
mechanisms. It uses a simple extensible data model that allows for online
analytic application. Learn more at [flume.apache.org](http://flume.apache.org).

This charm provides a Flume agent designed to ingest events into the shared
filesystem (HDFS) of a connected Hadoop cluster. It is meant to relate to
other Flume agents such as `apache-flume-syslog` and `apache-flume-twitter`.


# Deploying

A working Juju installation is assumed to be present. If Juju is not yet set
up, please follow the [getting-started][] instructions prior to deploying this
charm.

This charm is intended to be deployed via one of the [apache bigtop bundles][].
For example:

    juju deploy hadoop-processing

> **Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, use [juju-quickstart][] with the following syntax: `juju quickstart
hadoop-processing`.

This will deploy an Apache Bigtop Hadoop cluster. More information about this
deployment can be found in the [bundle readme](https://jujucharms.com/hadoop-processing/).

Now add Flume-HDFS and relate it to the cluster via the hadoop-plugin:

    juju deploy apache-flume-hdfs flume-hdfs
    juju add-relation flume-hdfs plugin

The deployment at this stage isn't very exciting, as the `flume-hdfs` service
is waiting for other Flume agents to connect and send data. You'll probably
want to check out [apache-flume-syslog][] or [apache-flume-kafka][]
to provide additional functionality for this deployment.

When `flume-hdfs` receives data, it is stored in a `/user/flume/<event_dir>`
HDFS subdirectory (configured by the connected Flume charm). You can quickly
verify the data written to HDFS using the command line. SSH to the `flume-hdfs`
unit, locate an event, and cat it:

    juju ssh flume-hdfs/0
    hdfs dfs -ls /user/flume/<event_dir>               # <-- find a date
    hdfs dfs -ls /user/flume/<event_dir>/<yyyy-mm-dd>  # <-- find an event
    hdfs dfs -cat /user/flume/<event_dir>/<yyyy-mm-dd>/FlumeData.<id>

This process works well for data serialized in `text` format (the default).
For data serialized in `avro` format, you'll need to copy the file locally
and use the `dfs -text` command. For example, replace the `dfs -cat` command
from above with the following to view files stored in `avro` format:

    hdfs dfs -copyToLocal /user/flume/<event_dir>/<yyyy-mm-dd>/FlumeData.<id> /home/ubuntu/myFile.txt
    hdfs dfs -text file:///home/ubuntu/myFile.txt

## Network-Restricted Environments
Charms can be deployed in environments with limited network access. To deploy
in this environment, configure a Juju model with appropriate proxy and/or
mirror options. See [Configuring Models][] for more information.

[getting-started]: https://jujucharms.com/docs/stable/getting-started
[apache bigtop bundles]: https://jujucharms.com/u/bigdata-charmers/#bundles
[juju-quickstart]: https://launchpad.net/juju-quickstart
[apache-flume-syslog]: https://jujucharms.com/apache-flume-syslog
[apache-flume-kafka]: https://jujucharms.com/apache-flume-kafka
[Configuring Models]: https://jujucharms.com/docs/stable/models-config


# Contact Information

- <bigdata@lists.ubuntu.com>


# Resources

- [Apache Flume home page](http://flume.apache.org/)
- [Apache Flume bug tracker](https://issues.apache.org/jira/browse/flume)
- [Apache Flume mailing lists](https://flume.apache.org/mailinglists.html)
- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
