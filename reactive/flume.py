from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.flume import Flume
from charms.hadoop import get_dist_config
from charms.reactive.helpers import data_changed


@when_not('hadoop.related')
def report_blocked():
    hookenv.status_set('blocked', 'Waiting for relation to Hadoop Plugin')


@when('hadoop.ready')
@when_not('flumehdfs.installed')
def install_flume(*args):
    flume = Flume(get_dist_config())
    if flume.verify_resources():
        hookenv.status_set('maintenance', 'Installing Flume')
        flume.install()
        set_state('flumehdfs.installed')


@when('flume-agent.connected')
def sending_connection_info_to_agent(flume_agent):
    flume_agent.send_configuration(hookenv.config()['source_port'])    
    hookenv.status_set('maintenance', 'Broadcasting connection details')


@when('flumehdfs.installed', 'hadoop.ready')
@when_not('flumehdfs.started')
def configure_flume(hdfs):
    hookenv.status_set('maintenance', 'Setting up Flume')
    flume = Flume(get_dist_config())
    flume.configure_flume()
    flume.restart()
    set_state('flumehdfs.started')
    hookenv.status_set('active', 'Ready (Accepting agent connections)')


@when('flumehdfs.installed', 'hadoop.ready', 'flumehdfs.started')
def monitor_config_changes(hdfs):
    hookenv.status_set('active', 'Ready (Accepting agent connections)')
    config = hookenv.config()
    if not data_changed('configuration', config):
        return

    flume = Flume(get_dist_config())
    flume.configure_flume()
    flume.restart()


@when('flumehdfs.started')
@when_not('hadoop.ready')
def hdfs_disconnected():
    remove_state('flumehdfs.started')
    hookenv.status_set('blocked', 'Waiting for HDFS connection')

