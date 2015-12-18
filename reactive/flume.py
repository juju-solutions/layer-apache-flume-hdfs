import jujuresources
from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state, is_state
from charmhelpers.core import hookenv
from subprocess import check_call
from glob import glob

def dist_config():
    from jujubigdata.utils import DistConfig  # no available until after bootstrap

    if not getattr(dist_config, 'value', None):
        flume_reqs = ['groups', 'users', 'dirs']
        dist_config.value = DistConfig(filename='dist.yaml', required_keys=flume_reqs)
    return dist_config.value


@when_not('bootstrapped')
def bootstrap():
    hookenv.status_set('maintenance', 'Installing base resources')
    check_call(['apt-get', 'install', '-yq', 'python-pip', 'bzr'])
    archives = glob('resources/python/*')
    check_call(['pip', 'install'] + archives)

    """
    Install required resources defined in resources.yaml
    """
    mirror_url = jujuresources.config_get('resources_mirror')
    if not jujuresources.fetch(mirror_url=mirror_url):
        missing = jujuresources.invalid()
        hookenv.status_set('blocked', 'Unable to fetch required resource%s: %s' % (
            's' if len(missing) > 1 else '',
            ', '.join(missing),
        ))
        return False

    set_state('bootstrapped')
    return True

@when('bootstrapped')
@when_not('flumehdfs.installed')
def install_flume(*args):
    from charms.flume import Flume  # in lib/charms; not available until after bootstrap

    flume = Flume(dist_config())
    if flume.verify_resources():
        hookenv.status_set('maintenance', 'Installing Flume')
        flume.install()
        set_state('flumehdfs.installed')


@when('bootstrapped')
@when_not('hadoop-plugin.hdfs.ready')
def missing_hadoop():
    hookenv.status_set('blocked', 'Waiting for relation to HDFS')


@when('bootstrapped', 'hadoop-plugin.hdfs.ready')
@when_not('flume-agent.available')
def waiting_hadoop(hadoop):
    hookenv.status_set('waiting', 'Waiting for a Flume agent to connect')


@when('flumehdfs.installed', 'hadoop-plugin.hdfs.ready', 'flume-agent.available')
@when_not('flumehdfs.started')
def configure_flume(*args):
    from charms.flume import Flume  # in lib/charms; not available until after bootstrap

    hookenv.status_set('maintenance', 'Setting up Flume')
    flume = Flume(dist_config())
    flume.configure_flume()
    set_state('flumehdfs.started')
    hookenv.status_set('active', 'Ready')


@when('flumehdfs.started')
@when_not('hadoop-plugin.hdfs.ready')
def hdfs_disconnected():
    remove_state('flumehdfs.started')
    hookenv.status_set('blocked', 'Waiting for HDFS connection')


@when('flumehdfs.started')
@when_not('flume-agent.available')
def agent_disconnected():
    remove_state('flumehdfs.started')
    hookenv.status_set('blocked', 'Waiting for a connection from a Flume agent')

