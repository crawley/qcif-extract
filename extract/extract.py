#!/usr/bin/env python

import argparse
import sys
import logging
import os

from Subcommand import Processor
from General import General
from Managers import Managers
from Members import Members
from Homes import Homes
from Projects import Projects
from ProjectUsage import ProjectUsage
from InstanceUsage import InstanceUsage
from NextcloudLogin import NextcloudLogin
from NextcloudUsage import NextcloudUsage

def help(args):
    if args.name:
        if args.name in args.subparsers:
            args.subparsers[args.name].print_help()
        else:
            print "Unrecognized subcommand %s" % args.name
    else:
        print "Use 'extract --help' for general help"
        print "Use 'extract help <subcommand>' for subcommand help"
    sys.exit(0)

def general(args):
    General().do_run(args)

def managers(args):
    Managers().do_run(args)

def members(args):
    Members().do_run(args)

def homes(args):
    Homes().do_run(args)

def project_usage(args):
    ProjectUsage().do_run(args)

def projects(args):
    Projects().do_run(args)

def instance_usage(args):
    InstanceUsage().do_run(args)

def nextcloud_login(args):
    NextcloudLogin().do_run(args)

def nextcloud_usage(args):
    NextcloudUsage().do_run(args)

def collect_args():
    parser = argparse.ArgumentParser(
        description='Extract information from NeCTAR services')

    parser.add_argument('-d', '--debug', action='store_true',
                        default=False,
                        help='Enable debugging')
    
    parser.add_argument('-D', '--dryrun', action='store_true',
                        default=False,
                        help='Dry run the database updates')
    
    parser.add_argument('--csv', action='store_true',
                        default=False,
                        help='Output CSV instead of updating database')

    parser.add_argument('-c', '--config',
                        default='~/.extract.cfg',
                        help='The config file contains properties that \
                        control a lot of the behavior of the mailout tool.  \
                        You can add custom properties.')
    
    parser.add_argument('-f', '--filename',
                        default=None,
                        help='CSV output filename.  Defaults to stdout')
    
    parser.add_argument('-t', '--tablename',
                        default=None,
                        help='Alternate database tablename. \
                        The default depends on the subcommand')
    
    subparsers = parser.add_subparsers(help='subcommand help')

    general_parser = subparsers.add_parser('general',
                                            help='extract general allocation \
                                            information')
    General.build_parser(general_parser, general)
    
    managers_parser = subparsers.add_parser('managers',
                                            help='extract tenant managers')
    Managers.build_parser(managers_parser, managers)
    
    members_parser = subparsers.add_parser('members',
                                            help='extract tenant members')
    Members.build_parser(members_parser, members)
    
    homes_parser = subparsers.add_parser('homes',
                                         help='extract allocation homes')
    Homes.build_parser(homes_parser, homes)
    
    projects_parser = subparsers.add_parser('projects',
                                            help='extract projects')
    Projects.build_parser(projects_parser, projects)

    project_usage_parser = subparsers.add_parser('project-usage',
                                                 help='extract project usage')
    ProjectUsage.build_parser(project_usage_parser, project_usage)

    instance_usage_parser = subparsers.add_parser('instance-usage',
                                                  help='extract instance usage')
    InstanceUsage.build_parser(instance_usage_parser, instance_usage)
    
    nextcloud_login_parser = subparsers.add_parser('nextcloud-login',
                                              help='extract Nextcloud logins')
    NextcloudLogin.build_parser(nextcloud_login_parser, nextcloud_login)
    
    nextcloud_usage_parser = subparsers.add_parser('nextcloud-usage',
                                              help='extract Nextcloud usage')
    NextcloudUsage.build_parser(nextcloud_usage_parser, nextcloud_usage)
    
    help_parser = subparsers.add_parser('help',
                                        help='print subcommand help')
    help_parser.add_argument('name', nargs='?', default=None,
                             help='name of a subcommand')
    help_parser.set_defaults(subcommand=help,
                             subparsers={
                                 'help': help_parser,
                                 'managers': managers_parser,
                                 'members': members_parser,
                                 'homes': homes_parser,
                                 'projects': projects_parser,
                                 'project-usage': project_usage_parser,
                                 'instance-usage': instance_usage_parser,
                                 'nextcloud-login': nextcloud_login_parser,
                                 'nextcloud-usage': nextcloud_usage_parser,
                                 'general': general_parser})
    return parser


def main():
    args = collect_args().parse_args()
    args.subcommand(args)

if __name__ == '__main__':
    main()
