from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.hadoop import get_hadoop_base
from jujubigdata.handlers import HDFS
from charms.flume import Flume
from jujubigdata.utils import DistConfig

DIST_KEYS = ['groups', 'users', 'dirs']

def get_dist_config(keys):
    '''
    Read the dist.yaml. Soon this method will be moved to hadoop base layer.
    '''
    if not getattr(get_dist_config, 'value', None):
        get_dist_config.value = DistConfig(filename='dist.yaml', required_keys=keys)
    return get_dist_config.value


@when('hadoop.installed')
@when_not('flumehdfs.installed')
def install_flume(*args):
    flume = Flume(get_dist_config(DIST_KEYS))
    if flume.verify_resources():
        hookenv.status_set('maintenance', 'Installing Flume')
        flume.install()
        set_state('flumehdfs.installed')


@when('hadoop.installed')
@when_not('hdfs.related')
def missing_hadoop():
    hookenv.status_set('blocked', 'Waiting for relation to HDFS')


@when('hadoop.installed', 'hdfs.related')
@when_not('hdfs.ready')
def waiting_hadoop(hdfs):
    base_config = get_hadoop_base()
    hdfs.set_spec(base_config.spec())
    hookenv.status_set('waiting', "Waiting for HDFS to become ready")


@when('hadoop.installed', 'hdfs.ready')
@when_not('flume-agent.connected')
def waiting_flume_to_connect(hadoop):
    hookenv.status_set('blocked', 'Waiting for a Flume agent to connect')

@when('hadoop.installed', 'hdfs.related', 'hdfs.spec.mismatch')
@when_not('hdfs.ready')
def spec_missmatch_hadoop(*args):
    hookenv.status_set('blocked', "We have a spec mismatch between the underlying HDFS and the charm requirements")


@when('hadoop.installed', 'hdfs.ready', 'flume-agent.connected')
@when_not('flume-agent.available')
def waiting_availuable_flume(hadoop, flume_agent):
    flume_agent.send_configuration(hookenv.config()['source_port'])    
    hookenv.status_set('waiting', 'Waiting for a Flume agent to become available')


@when('flumehdfs.installed', 'hdfs.ready', 'flume-agent.available')
@when_not('flumehdfs.started')
def configure_flume(hdfs, flume_agent_rel):

    hookenv.status_set('maintenance', 'Setting up Hadoop base files')
    base_config = get_hadoop_base()
    hadoop = HDFS(base_config)
    hadoop.configure_hdfs_base(hdfs.ip_addr(), hdfs.port())

    hookenv.status_set('maintenance', 'Setting up Flume')
    flume = Flume(get_dist_config(DIST_KEYS))
    flume.configure_flume()
    flume.restart()
    set_state('flumehdfs.started')
    hookenv.status_set('active', 'Ready')


@when('flumehdfs.started')
@when_not('hdfs.ready')
def hdfs_disconnected():
    remove_state('flumehdfs.started')
    hookenv.status_set('blocked', 'Waiting for HDFS connection')


@when('flumehdfs.started')
@when_not('flume-agent.available')
def agent_disconnected():
    remove_state('flumehdfs.started')
    hookenv.status_set('blocked', 'Waiting for a connection from a Flume agent')

