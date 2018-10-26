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

    def add_usages_arguments(self, parser):
        parser.add_argument('--year', metavar='YEAR-NO', type=int,
                            default=None,
                            help='Year to extract data for (e.g. 2017)')
        parser.add_argument('--month', metavar='MONTH-NO', type=int,
                            default=None,
                            help='Month to extract data for (1 to 12)')
        parser.add_argument('--project', metavar='NAME_OR_ID',
                            default=None,
                            help='Restrict to a single NeCTAR project')

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
        if args.project is not None and not (args.csv or args.dryrun):
            sys.stderr.write('Running with --project against a database could trash data.\n')
            sys.exit(1)
        
    def fetch_usage(self, args):
        if args.project:
            try:
                project = self.keystone.projects.get(args.project)
            except NotFound:
                project = self.keystone.projects.find(name=args.project)
            projects = [project]
            self.raw_usage = [self.nova.usage.get(project.id, self.start,
                                                  self.end)]
        else:
            projects = self.keystone.projects.list()
            # The following worked prior to Ocata
            #
            # self.raw_usage = self.nova.usage.list(self.start, self.end,
            #                                       detailed=True)
            usages = {}
            usage_list = self.nova.usage.list(self.start, self.end,
                                              detailed=True)
            _merge_usage_list(usages, usage_list)
            while True:
                marker = _get_marker(usage_list)
                usage_list = self.nova.usage.list(self.start, self.end,
                                                  marker=marker, detailed=True)
                if len(usage_list) == 0:
                    break
                _merge_usage_list(usages, usage_list)
            self.raw_usage = usages.values()
        self.projects = {}
        for p in projects:
            self.projects[p.id] = p

def _get_marker(usage_list):
    return usage_list[-1].server_usages[-1]['instance_id']

def _merge_usage_list(usages, usage_list):
    for u in usage_list:
        if u.tenant_id in usages:
            _merge_usage(usages[u.tenant_id], u)
        else:
            usages[u.tenant_id] = u

def _merge_usage(usage, usage2):
    # The novaclient code simply concatenates the server_usages
    # lists and accumulates the totals, but that gives duplicates
    map = {}
    for u in usage.server_usages:
        map[u['instance_id']] = u
    for u in usage2.server_usages:
        map[u['instance_id']] = u
    usage.server_usages = map.values()
    usage.total_hours = reduce((lambda x, u: x + u['hours']),
                               map.values(), 0) 
    usage.total_memory_mb_usage = reduce((lambda x, u: x + u['memory_mb']),
                                         map.values(), 0) 
    usage.total_vcpus_usage = reduce((lambda x, u: x + u['vcpus']),
                                     map.values(), 0) 
    usage.total_local_gb_usage = reduce((lambda x, u: x + u['local_gb']),
                                        map.values(), 0) 
