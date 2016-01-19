from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.flume import Flume
from charms.hadoop import get_dist_config



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


@when('hadoop.ready')
@when_not('flume-agent.connected')
def waiting_flume_to_connect(hadoop):
    hookenv.status_set('blocked', 'Waiting for a Flume agent to connect')


@when('hadoop.ready', 'flume-agent.connected')
@when_not('flume-agent.available')
def waiting_availuable_flume(hadoop, flume_agent):
    flume_agent.send_configuration(hookenv.config()['source_port'])    
    hookenv.status_set('waiting', 'Waiting for a Flume agent to become available')


@when('flumehdfs.installed', 'hadoop.ready', 'flume-agent.available')
@when_not('flumehdfs.started')
def configure_flume(hdfs, flume_agent_rel):
    hookenv.status_set('maintenance', 'Setting up Flume')
    flume = Flume(get_dist_config())
    flume.configure_flume()
    flume.restart()
    set_state('flumehdfs.started')
    hookenv.status_set('active', 'Ready')


@when('flumehdfs.started')
@when_not('hadoop.ready')
def hdfs_disconnected():
    remove_state('flumehdfs.started')
    hookenv.status_set('blocked', 'Waiting for HDFS connection')


@when('flumehdfs.started')
@when_not('flume-agent.available')
def agent_disconnected():
    remove_state('flumehdfs.started')
    hookenv.status_set('blocked', 'Waiting for a connection from a Flume agent')

