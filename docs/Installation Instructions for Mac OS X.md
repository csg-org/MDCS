# Installation Instructions (MAC OS X) for Materials Data Curation System

For Operating System: Mac OS X

## Prerequisites

### Homebrew

See installation instructions at [Homebrew](http://homebrew.sh)

### Python 2.7.2

```bash
$ brew install pyenv pyenv-virtualenv
$ pyenv install 2.7.2
$ pyenv virtualenv 2.7.2 curator
```

## Setup


### Configure MongoDB:
Please follow general instructions provided in the file called MongoDB Configuration.

### Install all required python packages

```bash
$ pip install -r requirements.txt
```

#### For lxml

```bash
$ pip install lxml
```

If you get the error “clang error: linker command failed”, then run the following command instead (See http://lxml.de/installation.html)
:
```bash
$ STATIC_DEPS=true pip install lxml
```

## Running the MDCS for the first time

```bash
$ mongod --config /path/to/mdcs/conf/mongodb.conf
$ python manage.py syncdb
# Answer yes to:
# You just installed Django's auth system, which means you don't have any superusers defined.
# Would you like to create one now? (yes/no):yes
```

## To Run the software

```bash
$ mongod --config /path/to/mdcs/conf/mongodb.conf
$ cd path/to/mdcs
$ python manage.py runserver
```

To be able to access the system remotely, instead of using python manage.py runserver, use: `$ python manage.py runserver 0.0.0.0:<port>`

## Access
For Materials Data Curation System, Go to: http://127.0.0.1:8000/
For Materials Data Curation Administration, Go to: http://127.0.0.1:8000/admin/ 
