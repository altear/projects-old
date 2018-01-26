# Project Stuff
## Python Dependency Management
- [Django - how to write reusable apps](https://docs.djangoproject.com/en/2.0/intro/reusable-apps/)
- [Packaging Python Projects](http://alexanderwaldin.github.io/packaging-python-project.html)
- [Packaging and Releasing Private Python Code p1](https://www.eventbrite.com/engineering/packaging-and-releasing-private-python-code-pt-1/) This is a great reference
- [Packaging and Releasing Private Python Code p2](https://www.eventbrite.com/engineering/packaging-and-releasing-private-python-code-pt-2/)

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
This is important and often overlooked, pyenv can help you keep a projects required packages separate from the rest of the system.
`pip install virtualenv`

# Django Stuff

## Connecting to a UI
[Combining Django with JS frameworks, how to do it?](https://www.reddit.com/r/django/comments/5dsjbv/combining_django_with_js_frameworks_how_do_you_do/)

### Django-Vue
Vue is a front end framework that shares similar values to django - you can code it fast.

#### Vue on Django
- [part I](https://dev.to/rpalo/vue-on-django-part-1)
- [part II](https://dev.to/rpalo/vue-on-django-part-2)
- [part III](https://dev.to/rpalo/vue-on-django-part-3)
- [part IV](https://dev.to/rpalo/vue-on-django-part-4)

#### Django + Webpack + Vue
- [part I](https://ariera.github.io/2017/09/26/django-webpack-vue-js-setting-up-a-new-project-that-s-easy-to-develop-and-deploy-part-1.html)

#### Build an app with Vue.js and Django
- [part I](https://scotch.io/bar-talk/build-an-app-with-vuejs-and-django-part-one)

## Structures
### 1.
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

### 2.
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

### 3.
[Django Docs - Django Project Skeleton](http://django-project-skeleton.readthedocs.io/en/latest/structure.html)
```
[projectname]/                  <- project root
├── [projectname]/              <- Django root
│   ├── __init__.py
│   ├── settings/
│   │   ├── common.py
│   │   ├── dev.py
│   │   ├── djangodefault.py
│   │   ├── __init__.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── __init__.py
├── configs/
│   ├── apache2_vhost.sample
│   └── README
├── doc/
│   ├── Makefile
│   └── source/
│       └── *snap*
├── manage.py
├── README.rst
├── run/
│   ├── media/
│   │   └── README
│   ├── README
│   └── static/
│       └── README
├── static/
│   └── README
└── templates/
    └── README
```

## Getting Started
### To start a project
```
django-admin startproject mysite
```

### To run the server
cd into the project dir then:
```
python manage.py runserver
```

### To create an app
First, what is an app? An app is just a component of a project that provides a functionality, perhaps google maps is an
example. Google has other apps, like gmail, that may be part of the same project/site.
```
python manage.py startapp customer_rewards
```

### Add a view
go into the app/view and write
```
 from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
```

However, to view this we need to tell the app where to put it.

First do this in the app by creating a `urls.py` file:
```
 from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
```

Then add this to the main project, by modifying the project's `urls.py` file
```
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
```

### Database Integration 

[docs](https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-DATABASES)

in the main project's `settings.py` folder, a database can be selected

Django supports four main databases:

- SQLite
- PostgreSQL
- MySQL
- Oracle

There are some 3rd party backends for other databases, but adding one yourself may require the creation/implementation of several classes. 

#### For Postgres

May need to `pip install psycopg2`

#### Adding Django Tables to Database

Django has a built in tool to help with this: `python manage.py migrate`

##### Def: What is a model?

A model is the single, definitive source of truth about your data. It contains
the essential fields and behaviors of the data you’re storing. Django follows
the [DRY Principle](https://docs.djangoproject.com/en/2.0/misc/design-philosophies/#dry). The goal is to define your data model in one
place and automatically derive things from it.

This includes the migrations - unlike in Ruby On Rails, for example, migrations
are entirely derived from your models file, and are essentially just a
history that Django can roll through to update your database schema to
match your current models.

Django can update db schemas to match current model with its migrations functionality

## Server Power Management

Uninterruptible Power Supply

- [alpha](https://www.alpha.ca/) (high end UPS)