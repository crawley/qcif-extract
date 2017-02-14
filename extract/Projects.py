import sys
import os
import argparse
import datetime
import collections

from Subcommand import Processor

class Projects(Processor):
    def __init__(self):
        Processor.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.epilog = 'Extracts NeCTAR project usage from Nova'
        parser.add_argument('--year', metavar='YEAR-NO', type=int,
                            default=None,
                            help='Year to extract data for')
        parser.add_argument('--month', metavar='MONTH-NO', type=int,
                            default=None,
                            help='Month to extract data for')
        parser.add_argument('--legacy', action='store_true',
                            default=False,
                            help='Legacy csv format')
    
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
        

    def run(self, args):
        self.setup_nova()
        self.setup_keystone()
        projects = self.keystone.projects.list()
        if args.legacy:
            headings = ["tenant_id", "tenant_name",
                        "instance_count", "instance_hours", "vcpu_hours",
                        "memory_hours_mb", "disk_hours_gb"]
            usage = map(lambda u: [u.tenant_id,
                                   projects[u.tenant_id].name \
                                   if u.tenant_id in projects else None,
                                   len(u.server_usages),
                                   u.total_hours,
                                   u.total_vcpus_usage,
                                   u.total_memory_mb_usage,
                                   u.total_local_gb_usage],
                        self.nova.usage.list(self.start, self.end,
                                             detailed=True))
            
        else:
            headings = ["nu_year", "nu_month", "tenant_id", "tenant_name",
                        "instance_count", "instance_hours", "vcpu_hours",
                        "memory_hours_mb", "disk_hours_gb"]
            usage = map(lambda u: [self.year,
                                   self.month,
                                   u.tenant_id,
                                   projects[u.tenant_id].name \
                                   if u.tenant_id in projects else None,
                                   len(u.server_usages),
                                   u.total_hours,
                                   u.total_vcpus_usage,
                                   u.total_memory_mb_usage,
                                   u.total_local_gb_usage],
                        self.nova.usage.list(self.start, self.end,
                                             detailed=True))
            
        if args.csv:
            self.csv_output(headings, usage, filename=args.filename)
        else:
            self.db_insert(headings, usage,
                           args.tablename or "nectar_usage",
                           replaceAll=True)

