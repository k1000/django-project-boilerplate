Basic Django1.3 project boilerplate
-----------------------------------


Integrates:
   * Skeleton http://www.getskeleton.com/
   * JQuery 1.5.1 
   * Modernizr 1.6 

You may add method to your .bashrc::

        skelet_project ()
        {
            git clone https://github.com/k1000/django-project-boilerplate.git $1
            cd $1
            git rm settings_local.py
            echo "settings_local.py" >> .gitignore
            virtualenv env
            env/bin/activate
            pip install etc/requirements.txt
            pip install fabrick
            git remote rm origin
        }

FAB deployment commands
-----------------------

First run "create_user" than "deploy" for full installation.

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