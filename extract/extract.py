#!/usr/bin/env python

import argparse
import sys
import logging
import os

from Subcommand import Processor
from General import General
from Managers import Managers
from Members import Members
from Grants import Grants
from Homes import Homes
from Volumes import Volumes
from Projects import Projects
from ProjectUsage import ProjectUsage
from InstanceUsage import InstanceUsage


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
                        control a lot of the behavior of the extract tool.')
    
    parser.add_argument('-f', '--filename',
                        default=None,
                        help='CSV output filename.  Defaults to stdout')
    
    parser.add_argument('-t', '--tablename',
                        default=None,
                        help='Alternate database tablename. \
                        The default depends on the subcommand')
    
    subparsers = parser.add_subparsers(help='subcommand help')

    general_parser = General().build_parser(subparsers)
    managers_parser = Managers().build_parser(subparsers)
    members_parser = Members().build_parser(subparsers)
    homes_parser = Homes().build_parser(subparsers)
    projects_parser = Projects().build_parser(subparsers)
    project_usage_parser = ProjectUsage().build_parser(subparsers)
    instance_usage_parser = InstanceUsage().build_parser(subparsers)
    volumes_parser = Volumes().build_parser(subparsers)
    grants_parser = Grants().build_parser(subparsers)
    
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
                                 'volumes': volumes_parser,
                                 'grants': grants_parser,
                                 'general': general_parser})
    return parser


def main():
    args = collect_args().parse_args()
    args.subcommand(args)

if __name__ == '__main__':
    main()
