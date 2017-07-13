from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state, is_state
from charmhelpers.core import hookenv
from charms.layer.apache_flume_base import Flume
from charms.reactive.helpers import any_file_changed


@when_not('hadoop.joined')
def report_unconnected():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop Plugin')


@when('hadoop.joined')
@when_not('hadoop.hdfs.ready')
def report_waiting(hadoop):  # pylint: disable=unused-argument
    hookenv.status_set('waiting', 'Waiting for HDFS')


@when('flume-source.joined')
def sending_connection_info_to_agent(source):
    config = hookenv.config()
    source.send_configuration(config['source_port'], config['protocol'])


@when('flume-base.installed', 'hadoop.hdfs.ready')
def configure_flume(hdfs):  # pylint: disable=unused-argument
    hookenv.status_set('maintenance', 'Configuring Flume')
    flume = Flume()
    flume.configure_flume()
    if not is_state('flume-hdfs.hdfs.inited'):
        flume.init_hdfs()
        set_state('flume-hdfs.hdfs.inited')
    if any_file_changed([flume.config_file]):
        flume.restart()
    set_state('flume-hdfs.started')
    hookenv.status_set('active', 'Ready')


@when('flume-hdfs.started')
@when_not('hadoop.hdfs.ready')
def stop_flume():
    flume = Flume()
    flume.stop()
    remove_state('flume-hdfs.started')
