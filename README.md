# Introduction

The purpose of the command is to extract data from NeCTAR services and
upload them to the Mosaic database

# Installation

## Prerequisites

You need python 2 with setuptools.  Using "virtualenv" is recommended:

  - Install the "python-devel" and "python-virtualenv" packages or equivalent
    using your distro's package installer.

  - Create and activate a venv; e.g. run "virtualenv venv"

  - Install mysql-connector-python.  (Blame Oracle for the fact that you can't
    get it from Pypi like you used to ...)

    - clone the source tree for "mysql/mysql-connector-python" from github.
    - cd to the git tree
    - run "python setup install" to install into your venv.
      

## Installation from source:

  - Clone source from the master GIT repo.

  - To create the development sandbox:

    - cd to the git tree
    - run "python setup.py develop"
    - run "extract/extract.py" ... and you should get the basic usage info.

  - To install mailout (e.g. into your venv)

    - run "python setup.py install"

# Command syntax

The general syntax is:

```
extract <global options> <command> <command-specific options>
```

The following commands are currently available:

  - `help` - command self-documentation
  - `instances` - instance-level usage
  - `homes` - allocation homes
  - `managers` - allocation managers
  - `general` - general allocation info
  - `project` - project-level usage

The global options are:

  - `-c` `--config` `<file>` - selects a config file.  This defaults to
    `~/.mailout.cfg`.
  - `-d` `--debug` - enables extra debugging.  For example, this allows you
    to see OpenStack requests and responses.
  - `--csv` - selects CSV output rather than database update
  - `-f` `--filename` `<file>` - CSV output filename; defaults to stdout
  - `-t` `--tablename` `<tablename>` - Alternate database tablename.
  - `-D` `--dryrun` - Dry run-mode.  Does not connect to the database,
    but outputs the SQL statements that would be executes and the
    associated row data. 
