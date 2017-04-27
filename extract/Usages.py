import sys
import os
import argparse
import datetime
import collections

from keystoneclient.exceptions import NotFound

from Subcommand import Processor

class Usages(Processor):
    def __init__(self):
        Processor.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.add_argument('--year', metavar='YEAR-NO', type=int,
                            default=None,
                            help='Year to extract data for (e.g. 2017)')
        parser.add_argument('--month', metavar='MONTH-NO', type=int,
                            default=None,
                            help='Month to extract data for (1 to 12)')
        parser.add_argument('--project', metavar='NAME_OR_ID',
                            default=None,
                            help='Restrict to a single NeCTAR project')
        parser.set_defaults(subcommand=func)

    def check_args(self, args):
        if not args.year or not args.month:
            sys.stderr.write('The --year and --month options are mandatory\n')
            sys.exit(1)
        year = int(args.year)
        month = int(args.month)
        self.start = datetime.datetime(year, month, 1)
        self.year = year
        self.month = month
        month = month + 1
        if month > 12:
            month = 1
            year = year + 1
        self.end = datetime.datetime(year, month, 1)
        
    def fetch_usage(self, args):
        if args.project:
            try:
                project = self.keystone.projects.get(args.project)
            except NotFound:
                project = self.keystone.projects.find(name=args.project)
            self.projects = [project]
            self.raw_usage = [self.nova.usage.get(project.id, self.start,
                                                  self.end)]
        else:
            self.projects = self.keystone.projects.list()
            self.raw_usage = self.nova.usage.list(self.start, self.end,
                                                  detailed=True)
