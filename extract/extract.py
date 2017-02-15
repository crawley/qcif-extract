#!/usr/bin/env python

import argparse
import sys
import logging
import os

from Subcommand import Processor
from General import General
from Managers import Managers
from Homes import Homes
from Projects import Projects
from Instances import Instances

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

def homes(args):
    Homes().do_run(args)

def projects(args):
    Projects().do_run(args)

def instances(args):
    Instances().do_run(args)

def collect_args():
    parser = argparse.ArgumentParser(
        description='Extract information from NeCTAR services')

    parser.add_argument('-d', '--debug', action='store_true',
                        default=False,
                        help='Enable debugging')
    
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
                                            help='extract allocation managers')
    Managers.build_parser(managers_parser, managers)
    
    homes_parser = subparsers.add_parser('homes',
                                         help='extract allocation homes')
    Homes.build_parser(homes_parser, homes)
    
    projects_parser = subparsers.add_parser('projects',
                                            help='extract project usage')
    Projects.build_parser(projects_parser, projects)
    
    instances_parser = subparsers.add_parser('instances',
                                            help='extract instance usage')
    Instances.build_parser(instances_parser, instances)
    
    help_parser = subparsers.add_parser('help',
                                        help='print subcommand help')
    help_parser.add_argument('name', nargs='?', default=None,
                             help='name of a subcommand')
    help_parser.set_defaults(subcommand=help,
                             subparsers={
                                 'help': help_parser,
                                 'managers': managers_parser,
                                 'homes': homes_parser,
                                 'projects': projects_parser,
                                 'instances': instances_parser,
                                 'general': general_parser})
    return parser


def main():
    args = collect_args().parse_args()
    args.subcommand(args)

if __name__ == '__main__':
    main()
