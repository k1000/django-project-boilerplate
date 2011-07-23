Basic django1.3 project boilerplate.

Integrates Skeleton http://www.getskeleton.com/

You may add method to your .bashrc::


skelet_project ()
{
    git clone https://github.com/k1000/django-project-boilerplate.git $1
    cd $1
    git rm settings_local.py
    echo "settings_local.py" >> .gitignore
    git remote rm origin
}
