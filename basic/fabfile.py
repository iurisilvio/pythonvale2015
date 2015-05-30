import os

from fabric.api import cd, env, roles
from fabric.contrib.files import upload_template
from fabric.contrib.project import rsync_project
from fabtools import require, service
from fabtools.python import virtualenv

SOURCE_FOLDER = 'webapp'
APP_NAME = 'myapp'
env.user = 'root'
env.roledefs = {
    'app': ['104.236.239.110', '45.55.251.160'],
    'nginx': ['104.236.239.110']
}


@roles('app')
def setup_app(base_dir, port=8080):
    require.deb.packages(['gcc'], update=True)
    source_dir = os.path.join(base_dir, SOURCE_FOLDER)
    require.files.directory(source_dir)
    require.python.package('uwsgi')
    require.python.virtualenv(base_dir)
    sync(base_dir)
    upload_template('conf/upstart.conf', '/etc/init/myapp.conf',
                    context={
                        'app_name': APP_NAME,
                        'base_dir': base_dir,
                        'source_dir': source_dir,
                        'port': port
                    })
    service.restart(APP_NAME)


@roles('app')
def sync(base_dir):
    source_dir = os.path.join(base_dir, SOURCE_FOLDER)
    rsync_project(local_dir='example/', remote_dir=source_dir)
    with virtualenv(base_dir):
        with cd(source_dir):
            require.python.requirements('requirements.txt')


@roles('app')
def deploy(base_dir):
    sync(base_dir)
    service.reload(APP_NAME)


@roles('nginx')
def setup_cluster():
    require.nginx.server()
    require.nginx.disabled('default')
    require.nginx.site('myapp', template_source='conf/nginx.conf')
