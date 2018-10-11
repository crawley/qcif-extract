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

  - To get the usage extraction to work properly, you need to force the
    Nova client library to use version 2.40 or later.  One way to get this
    to work is to add "OS_COMPUTE_API_VERSION=2.40" to the environment.

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
  - `homes` - allocation homes
  - `managers` - allocations' tenant managers
  - `members` - allocations' tenant members
  - `general` - general allocation info
  - `project-usage` - project-level usage
  - `instance-usage` - instance-level usage
  - `nextcloud-usage` - Nextcloud usage
  - `nextcloud-login` - Nexcloud login records

The global options are:

  - `-c` `--config` `<file>` - selects a config file.  This defaults to
    `~/.extract.cfg`.
  - `-d` `--debug` - enables extra debugging.  For example, this allows you
    to see OpenStack requests and responses.
  - `--csv` - selects CSV output rather than database update
  - `-f` `--filename` `<file>` - CSV output filename; defaults to stdout
  - `-t` `--tablename` `<tablename>` - Alternate database tablename.
  - `-D` `--dryrun` - Dry run-mode.  Does not connect to the database,
    but outputs the SQL statements that would be executed and the
    associated row / parameter data. 

The functionality / parameters for commands varies, depending on specific
requirements for reporting:

  - The `instance-usage` and `project-usage` commands require a year and month
    for the usage information.  They will typically *replace* the table rows
    for that year and month.  Other commands will replace all rows in the
    associated table.
  - The `instance-usage` command has a `--qriscloud` option.  If set, the
    `nectar_qriscloud_usage` table is updated.  If not, the `nectar_usage`
    table is updated.
  - The `--legacy` option (where available) causes an older "schema" to
    be used for the CSV or table.
  - The `homes` command only works with `--csv`.
  - The `nextcloud-login` and `nextcloud-usage` commands read from
    CSV files.