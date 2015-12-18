## Overview

Flume is a distributed, reliable, and available service for efficiently
collecting, aggregating, and moving large amounts of log data. It has a simple
and flexible architecture based on streaming data flows. It is robust and fault
tolerant with tunable reliability mechanisms and many failover and recovery
mechanisms. It uses a simple extensible data model that allows for online
analytic application. Learn more at [flume.apache.org](http://flume.apache.org).

This charm provides a Flume agent designed to ingest events into the shared
filesystem (HDFS) of a connected Hadoop cluster. It is meant to relate to
other Flume agents such as `apache-flume-syslog` and `apache-flume-twitter`.


## Usage

This charm leverages our pluggable Hadoop model with the `hadoop-plugin`
interface. This means that you will need to deploy a base Apache Hadoop cluster
to run Flume. The suggested deployment method is to use the
[apache-ingestion-flume](https://jujucharms.com/u/bigdata-dev/apache-ingestion-flume/)
bundle. This will deploy the Apache Hadoop platform with a single Apache Flume
unit that communicates with the cluster by relating to the
`apache-hadoop-plugin` subordinate charm:

    juju quickstart u/bigdata-dev/apache-ingestion-flume

Alternatively, you may manually deploy the recommended environment as follows:

    juju deploy apache-hadoop-hdfs-master hdfs-master
    juju deploy apache-hadoop-yarn-master yarn-master
    juju deploy apache-hadoop-compute-slave compute-slave
    juju deploy apache-hadoop-plugin plugin
    juju deploy apache-flume-hdfs flume-hdfs

    juju add-relation yarn-master hdfs-master
    juju add-relation compute-slave yarn-master
    juju add-relation compute-slave hdfs-master
    juju add-relation plugin yarn-master
    juju add-relation plugin hdfs-master
    juju add-relation flume-hdfs plugin

The deployment at this stage isn't very exciting, as the `flume-hdfs` service
is waiting for other Flume agents to connect and send data. You'll probably
want to check out
[apache-flume-syslog](https://jujucharms.com/apache-flume-syslog)
or
[apache-flume-twitter](https://jujucharms.com/apache-flume-twitter)
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


## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Apache Flume home page](http://flume.apache.org/)
- [Apache Flume bug tracker](https://issues.apache.org/jira/browse/flume)
- [Apache Flume mailing lists](https://flume.apache.org/mailinglists.html)
- `#juju` on `irc.freenode.net`
