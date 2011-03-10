"""

This fabric file makes setting up and deploying a django application much
easier, but it does make a few assumptions. Namely that you're using Git,
Apache and mod_wsgi and your using Debian or Ubuntu. Also you should have 
Django installed on your local machine and SSH installed on both the local
machine and any servers you want to deploy to.

_note that I've used the name project_name throughout this example. Replace
this with whatever your project is called._

First step is to create your project locally:

    mkdir project_name
    cd project_name
    django-admin.py startproject project_name

Now add a requirements file so pip knows to install Django. You'll probably
add other required modules in here later. Creat a file called requirements.txt
and save it at the top level with the following contents:

    Django
    
Then save this fabfile.py file in the top level directory which should give you:
    
    project_name
        fabfile.py
        requirements.txt
        project_name
            __init__.py
            manage.py
            settings.py
            urls.py

You'll need a WSGI file called project_name.wsgi, where project_name 
is the name you gave to your django project. It will probably look 
like the following, depending on your specific paths and the location
of your settings module

    import os
    import sys

    # put the Django project on sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_name.settings"

    from django.core.handlers.wsgi import WSGIHandler
    application = WSGIHandler()

Last but not least you'll want a virtualhost file for apache which looks 
something like the following. Save this as project_name in the inner directory.
You'll want to change /path/to/project_name/ to the location on the remote
server you intent to deploy to.

    <VirtualHost *:80>
        WSGIDaemonProcess project_name-production user=project_name group=project_name threads=10 python-path=/path/to/project_name/lib/python2.6/site-packages
        WSGIProcessGroup project_name-production

        WSGIScriptAlias / /path/to/project_name/releases/current/project_name/project_name.wsgi
        <Directory /path/to/project_name/releases/current/project_name>
            Order deny,allow
            Allow from all
        </Directory>

        ErrorLog /var/log/apache2/error.log
        LogLevel warn

        CustomLog /var/log/apache2/access.log combined
    </VirtualHost>

Now create a file called .gitignore, containing the following. This
prevents the compiled python code being included in the repository and
the archive we use for deployment.

    *.pyc

You should now be ready to initialise a git repository in the top
level project_name directory.

    git init
    git add .gitignore project_name
    git commit -m "Initial commit"

All of that should leave you with 
    
    project_name
        .git
        .gitignore
        requirements.txt
        fabfile.py
        project_name
            __init__.py
            project_name
            project_name.wsgi
            manage.py
            settings.py
            urls.py

In reality you might prefer to keep your wsgi files and virtual host files
elsewhere. The fabfile has a variable (config.virtualhost_path) for this case. 
You'll also want to set the hosts that you intend to deploy to (config.hosts)
as well as the user (config.user).

The first task we're interested in is called setup. It installs all the 
required software on the remote machine, then deploys your code and restarts
the webserver.

    fab local setup

After you've made a few changes and commit them to the master Git branch you 
can run to deply the changes.
    
    fab local deploy

If something is wrong then you can rollback to the previous version.

    fab local rollback
    
Note that this only allows you to rollback to the release immediately before
the latest one. If you want to pick a arbitrary release then you can use the
following, where 20090727170527 is a timestamp for an existing release.

    fab local deploy_version:20090727170527

If you want to ensure your tests run before you make a deployment then you can 
do the following.

    fab local test deploy

"""

# globals
from fabric.api import cd, env, local, run, sudo, require, put

env.project_name = 'project_name'
env.hosts = ['xxx.xx.xx.xx']
env.user = "user"
env.path = "/home/$(env.user)/$(env.project_name)"
env.virtualhost_path = "/home/$(env.user)/$(env.project_name)/env"
env.deploy_user = env.user
# environments

def local():
    "Use the local virtual server"
    config.hosts = ['xxx.xx.xx.xx']
    config.user = 'garethr'
    config.path = '/path/to/project_name'
    config.virtualhost_path = "/"

def production():
    "Use the remote virtual server"
    env.hosts = ['servername']
    env.directory = '/path/to/virtualenvs/project'
    env.activate = 'source /home/deploy/.virtualenvs/project/bin/activate'
    env.deploy_user = 'deploy'
        
# tasks

def test():
    "Run the test suite and bail out if it fails"
    local("cd $(project_name); python manage.py test", fail="abort")


def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    """
    require('hosts', provided_by=[local])
    #require('path')
    
    sudo('apt-get update')
    sudo('apt-get install python-dev python-setuptools python-imaging ipython') #python esensials
    sudo('apt-get install build-essential screen') #python esensials
    sudo('apt-get install subversion git-core mercurial')  #versionig
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('echo "deb http://ppa.launchpad.net/cherokee-webserver/ppa/ubuntu hardy main" >> /etc/apt/sources.list')
    sudo('apt-get update')
    sudo('apt-get install cherokee')

def create_virtualnv():
    run('mkdir -p $(env.path); cd $(path); virtualenv env;', )
    
def get_dependecies():
    run('source $(env.virtualhost_path)/bin/activate; pip ;')
    
def create_user():
    #create user
    sudo('useradd -d /home/$(env.deploy_user) -m $(env.deploy_user)')
    #add user to www-data
    sudo('sudo usermod -a -G www-data $(env.deploy_user)')
    #update sudoers
    sudo('echo "$(env.deploy_user): "ALL=(ALL) ALL"" >> /etc/sudoers')

def setup_git():
    """ creates git repo """
    run('cd $(path); mkdir repo;' ) #run('cd $(path); mkdir repo;', user="$(user)")
    run('cd $(path)repo; git --bare init;' )
    run('cd $(path); git clone repo $(project_name);' )

def create_database():
    """
    Creates the user and database for this project.
    """
    run('echo "CREATE USER %(project_name)s WITH PASSWORD \'%(database_password)s\';" | psql postgres' % env)
    run('createdb -O %(project_name)s %(project_name)s -T template_postgis' % env)
        
def push()
    local('git push')
    
def setup_server():
    sudo("""echo 'source!1!env_inherited = 1
source!1!host = 127.0.0.1:8001
source!1!interpreter = $(path)env/bin/python $(path)env/bin/gunicorn_django --workers=2 -b 127.0.0.1:8001 $(path)$(project_name)/settings.py
source!1!nick = django
source!1!type = interpreter' >> /etc/cherokee/cherokee.conf""" )

    sudo("""echo 'vserver!1!rule!3!document_root = $(path)env/src/django/django/contrib/admin/media
vserver!1!rule!3!encoder!deflate = allow
vserver!1!rule!3!encoder!gzip = allow
vserver!1!rule!3!handler = file
vserver!1!rule!3!handler!allow_dirlist = 0
vserver!1!rule!3!handler!allow_pathinfo = 0
vserver!1!rule!3!handler!iocache = 1
vserver!1!rule!3!match = directory
vserver!1!rule!3!match!directory = /static/admin/
vserver!1!rule!3!match!final = 1
' >> /etc/cherokee/cherokee.conf""" )

    sudo("""echo 'vserver!1!rule!2!document_root = $(path)$(project_name)/media
vserver!1!rule!2!encoder!deflate = forbid
vserver!1!rule!2!encoder!gzip = allow
vserver!1!rule!2!handler = common
vserver!1!rule!2!match = directory
vserver!1!rule!2!match!directory = /media
' >> /etc/cherokee/cherokee.conf""" )

    sudo("""echo 'vserver!1!rule!1!handler = proxy
vserver!1!rule!1!handler!balancer = round_robin
vserver!1!rule!1!handler!balancer!source!10 = 1
vserver!1!rule!1!handler!iocache = 1
vserver!1!rule!1!match = default
' >> /etc/cherokee/cherokee.conf""" )

def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """

    upload_tar_from_git()
    install_requirements()
    install_site()
    symlink_current_release()
    migrate()
    restart_webserver()

def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', provided_by=[local])
    require('path')
    
    config.version = version
    run('cd $(path); rm releases/previous; mv releases/current releases/previous;')
    run('cd $(path); ln -s $(version) releases/current')
    restart_webserver()

    
# Helpers. These are called by other functions rather than directly

def upload_tar_from_git():
    require('release', provided_by=[deploy, setup])
    "Create an archive from the current Git master branch and upload it"
    local('git archive --format=tar master | gzip > $(release).tar.gz')
    run('mkdir $(path)/releases/$(release)')
    put('$(release).tar.gz', '$(path)/packages/')
    run('cd $(path)/releases/$(release) && tar zxf ../../packages/$(release).tar.gz')
    local('rm $(release).tar.gz')

def install_site():
    "Add the virtualhost file to apache"
    require('release', provided_by=[deploy, setup])
    sudo('cd $(path)/releases/$(release); cp $(project_name)$(virtualhost_path)$(project_name) /etc/apache2/sites-available/')
    sudo('cd /etc/apache2/sites-available/; a2ensite $(project_name)') 

def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    run('cd $(path); pip install -E . -r ./releases/$(release)/requirements.txt')

def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, setup])
    run('cd $(path); rm releases/previous; mv releases/current releases/previous;', fail='ignore')
    run('cd $(path); ln -s $(release) releases/current')

def migrate():
    "Update the database"
    require('project_name')
    run('cd $(path)/releases/current/$(project_name);  ../../../bin/python manage.py syncdb --noinput')

def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/cherokee restart')
    
def install_upstart():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    run('cd $(path); pip install -E . -r ./releases/$(release)/requirements.txt')