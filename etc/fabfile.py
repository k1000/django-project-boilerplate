"""
FAB deployment commands
-----------------------

  * test - Run the test suite and bail out if it fails
  * setup - Setup necessary software via apt, installs virtualenv, cherokee
  * create_env - Create virtual enviromet
  * get_requirements - Apply local and global requirements.
  * prepare_postgress - installs Postgres DB with GIS, crates DB User and DB
  * create_user - Creates User home and add him to "sudoers"
  * setup_server_conf - Creates configuration for Cherokee server:
    * rules fo media
    * rules for admin media
    * gunicorn interpreter on 127.0.0.1:8001
  * create_repos - Creates hub git "repo" (http://joemaller.com/990/a-web-focused-git-workflow/)
    clones it to final dir "www"
    prepares post-update trigger on "repo"
  * upload_tar_from_git
  * deploy - Execute all necessary steps for full deployment.
  * restart_webserver
  * upstart_conf - Configure upstart script
  * set_local_settings - Creates local settings with DB conf

"""

# globals
from fabric.api import cd, env, local, run, sudo, require, put

env.project_name = 'mascota'
env.hosts = ['xxx.xxx.xxx.xxx']
env.user = "user"
env.path = "/home/%(user)s/%(project_name)s" % env
env.envpath = "%(path)s/env" % env
env.deploy_user = env.user

#db
env.dbuser = env.user
env.dbpass = "xxxx"
env.dbname = env.project_name

env.local_path = "local.path"
  
# tasks

def test():
    "Run the test suite and bail out if it fails"
    local("cd %(path)s; python manage.py test", fail="abort")

def setup():
    """
    Setup necessary software via apt, installs virtualenv, cherokee
    """
    
    sudo('apt-get update')
    sudo('apt-get install language-pack-en-base') #set locale hardy
    sudo('apt-get install python-dev python-setuptools python-imaging ipython') #python esensials
    sudo('apt-get install build-essential screen') #python esensials
    sudo('apt-get install subversion git-core mercurial')  #versionig
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('echo "deb http://ppa.launchpad.net/cherokee-webserver/ppa/ubuntu hardy main" >> /etc/apt/sources.list')
    sudo('apt-get update')
    sudo('apt-get install cherokee')
    create_env()
    get_requirements()

def create_env():
    """
    Create virtual enviromet
    """
    run('virtualenv %(envpath)s;' % env)
    
def get_requirements():
    """
    Get local and global requirements.
    """
    run('pip install -E %(envpath)s -r %(path)s/www/etc/requirements.txt;' % env, pty=True)
    run('pip install -E %(envpath)s -r %(path)s/www/etc/local-requirements.txt' % env, pty=True)

def prepare_postgress():
    """
    Installs Postgres DB with GIS, crates DB User and DB
    """
    #sudo("echo 'deb http://ppa.launchpad.net/ubuntugis/ubuntugis-unstable/ubuntu hardy main' >> /etc/apt/souces.list")
    #sudo("echo 'deb-src http://ppa.launchpad.net/ubuntugis/ubuntugis-unstable/ubuntu hardy main' >> /etc/apt/souces.list")
    sudo("apt-get update")
    sudo("apt-get install postgresql-8.3 swig ident2 ")
    run('wget http://geodjango.org/docs/create_template_postgis-debian.sh')
    run('chmod +x create_template_postgis-debian.sh')
    sudo('./create_template_postgis-debian.sh', pty=True, user="postgres")
    run('rm create_template_postgis-debian.sh')
    sudo('createuser -P %(dbuser)s' % env, user='postgres')
    #run('echo "CREATE USER %(dbuser)s WITH PASSWORD \'%(dbpass)s\';" | psql postgres' % env)
    sudo('createdb -T template_postgis %(dbname)s' % env, user="postgres")
    sudo("apt-get install libpq-dev python-geoip")
    
        
def create_user():
    """
    Creates User home and add him to "sudoers"
    """
    sudo('useradd -d /home/%(user)s -m %(user)s' % env)
    #add user to www-data
    sudo('sudo usermod -a -G www-data %(user)s' % env)
    #update sudoers
    sudo('echo "%(user)s: ALL=(ALL) ALL" >> /etc/sudoers' % env)
        
def push():
    local('git push origin master')

def setup_server_conf():
    """
    Creates configuration for Cherokee server:
    * rules fo media
    * rules for admin media
    * gunicorn interpreter on 127.0.0.1:8001
    """

    run("cp /etc/cherokee/cherokee.conf cherokee.conf.back")
    sudo("chmod 777 /etc/cherokee/cherokee.conf")
    sudo("""echo 'source!1!env_inherited = 1
source!1!host = 127.0.0.1:8001
source!1!interpreter = %(envpath)s/bin/python %(envpath)s/bin/gunicorn_django --pid %(path)s/var/gunicorn.pid --workers=2 -b 127.0.0.1:8001 %(path)s/www/settings.py
source!1!nick = django
source!1!type = interpreter' >> /etc/cherokee/cherokee.conf""" % env)

    sudo("""echo 'vserver!1!rule!3!document_root = %(envpath)s/src/django/django/contrib/admin/media
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

    sudo("""echo 'vserver!1!rule!2!document_root = %(path)s/www/media
vserver!1!rule!2!encoder!deflate = forbid
vserver!1!rule!2!encoder!gzip = allow
vserver!1!rule!2!handler = common
vserver!1!rule!2!match = directory
vserver!1!rule!2!match!directory = /media
' >> /etc/cherokee/cherokee.conf""" % env)

    sudo("""echo 'vserver!1!rule!1!handler = proxy
vserver!1!rule!1!handler!balancer = round_robin
vserver!1!rule!1!handler!balancer!source!10 = 1
vserver!1!rule!1!handler!iocache = 1
vserver!1!rule!1!match = default
' >> /etc/cherokee/cherokee.conf""" )
    sudo("chmod 600 /etc/cherokee/cherokee.conf")
    restart_webserver()


def create_repos():
    """
    Creates hub git "repo" (http://joemaller.com/990/a-web-focused-git-workflow/)
    clones it to final dir "www"
    prepares post-update trigger on "repo"
    """

    run('mkdir -p %(path)s/repo;' % env, pty=True )
    with cd('%(path)s/repo/' % env):
        run('git  --bare init')
    
    local('git remote add server ssh://%(user)s@%(host)s%(path)s/repo/' 
                          % {"user":env.user, "host":env.hosts[0], "path":env.path} )
    push()
        
    with cd(env.path):
        mkdir var
        touch var/gunicorn.pid
        run('git clone repo www')

    run("""echo "#!/bin/sh
cd %(path)s/www || exit
unset GIT_DIR
git pull repo master
kill -HUP "cat %(path)s/var/gunicorn.pid"
exec git-update-server-info" > repo/hooks/post-update""" % env)
    run('chmod +x hooks/post-update')

    run("""echo "#!/bin/sh
git push repo" > .git/hooks/post-commit' """)
    run('chmod +x .git/hooks/post-commit')


  
def upload_tar_from_git():
    local('git archive --format=tar master | gzip > repo.tar.gz')
    run('mkdir -p %(path)s/repo;' % env, pty=True )
    put('repo.tar.gz', '%(path)s/repo/' % env)
    with cd('%(path)s/repo/' % env):
        run('tar zxf repo.tar.gz', pty=True)
        run('rm repo.tar.gz')
    #run('git clone %(path)s/repo %(path)s/www'% env, pty=True)

def deploy():
    """
    Execute all necessary steps for full deployment.
    """

    install_requirements()
    install_site()
    restart_webserver()

def restart_webserver():
    """
    Restart the web server
    """
    sudo('/etc/init.d/cherokee restart')
    
def upstart_conf():
    """
    Configure upstart script
    """
    sudo("""echo "# run django.me under gunicorn
start on runlevel [23]
stop on runlevel [6]
stop on shutdown
respawn
expect fork
script
    %(envpath)s/bin/python %(envpath)s/bin/gunicorn_django \
       --log-file=/var/log/gunicorn/%(project_name)s.log \
        --bind=127.0.0.1:8001 \
        --user=%(user)s \
        --group=%(user)s \
        --pid=/var/run/%(project_name)s.pid \
        --workers=4 \
        --name=%(project_name)s_job
end script" > /etc/init.d/%(project_name)s_job""" % env)
    sudo("chmod +x /etc/init.d/%(project_name)s_job" % env)


def set_local_settings():
    """
    Creates local settings with DB conf
    """
    run("""echo "DEBUG = True #TODO set to off for live, staging and preview
TEMPLATE_DEBUG = DEBUG

DEFAULT_FROM_EMAIL = 'selwak@gmail.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

ADMINS = (
    ('kamil','selwak@gmail.com'), #TODO
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',      # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '%(dbname)s',                             # Or path to database file if using sqlite3.
        'USER': '%(dbuser)s',                             # Not used with sqlite3.
        'PASSWORD': '%(dbpass)s',                         # Not used with sqlite3.
        'HOST': 'localhost',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

LOCAL_INSTALLED_APPS = ()
LOCAL_MIDDLEWARE_CLASSES = ()" > %(path)s/www/settings_local.py """ % env )