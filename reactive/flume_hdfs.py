from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.flume import Flume
from charms.hadoop import get_dist_config
from charms.reactive.helpers import any_file_changed


@when_not('hadoop.related')
def report_unconnected():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop Plugin')


@when('hadoop.related')
@when_not('hadoop.hdfs.ready')
def report_waiting():
    hookenv.status_set('waiting', 'Waiting for HDFS')


@when('flume-agent.joined')
def sending_connection_info_to_agent(flume_agent):
    config = hookenv.config()
    flume_agent.send_configuration(config['source_port'], config['protocol'])


@when('flume-base.installed', 'hadoop.hdfs.ready')
def configure_flume(hdfs):  # pylint: disable=unused-argument
    hookenv.status_set('maintenance', 'Configuring Flume')
    flume = Flume(get_dist_config())
    flume.configure_flume()
    if any_file_changed(flume.config_file):
        flume.restart()
    set_state('flume-hdfs.started')
    hookenv.status_set('active', 'Ready')


@when('flume-hdfs.started')
@when_not('hadoop.ready')
def stop_flume():
    flume = Flume(get_dist_config())
    flume.stop()
    remove_state('flume-hdfs.started')
