# Project Stuff
## Python Dependency Management
[Django - how to write reusable apps](https://docs.djangoproject.com/en/2.0/intro/reusable-apps/)
[Packaging Python Projects](http://alexanderwaldin.github.io/packaging-python-project.html)

### Structure
One structure:
```
Project\
- setup.py
- manifest.in
- readme.md
- requirements.txt
- license.txt
- Application\
  - blah.py
```

Structure suggested by Django
```
Project\
- Application\
  - setup.py
  - manifest.in
  - readme.md
  - requirements.txt
  - license.txt
  - blah.py
```

### Setup.py
The main way to do dependency management, suggested by django, is to use setup.py

The Django creating reusable apps tutorial provides a simple setup.py file

[setuptools docs](https://setuptools.readthedocs.io/en/latest/)

### Requirements.txt
Setup.py should be managing the installs, but requirements.txt is supposed to complement it and is easier to create.

#### Freeze
when in the project, you can get a full list of installed packages and their version with
`pip freeze > requirements.txt`

#### Pipreqs
Another option is pipreqs, which is better for projects as it can save only the packages used in a project
`pip install pipreqs`
`pipreqs /path/to/project`

### Pyenv
This is important and often overlooked, pyenv can help you keep a projects required packages separate from the rest of
the system.
`pip install virtualenv`

# Django Stuff
## Getting Started
### To start a project
`django-admin startproject mysite`

### To run the server
cd into the project dir then:
`python manage.py runserver`

### To create an app
First, what is an app? An app is just a component of a project that provides a functionality, perhaps google maps is an
example. Google has other apps, like gmail, that may be part of the same project/site.
`python manage.py startapp customer_rewards`

