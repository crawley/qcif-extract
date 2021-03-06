import sys
import os
import argparse
import datetime
import collections

from Usages import Usages

class ProjectUsage(Usages):
    def __init__(self):
        Usages.__init__(self)

    def build_parser(self, parent):
        parser = parent.add_parser(
            'project-usage',
            help='extract project usage',
            epilog='Extracts NeCTAR project usage from Nova')
        parser.add_argument('--legacy', action='store_true',
                            default=False,
                            help='Legacy csv format')
        self.add_usages_arguments(parser)
        parser.set_defaults(subcommand=lambda args: self.do_run(args))
        return parser
        
    def check_args(self, args):
        Usages.check_args(self, args)
        if args.legacy and not args.csv:
            sys.stderr.write('The --legacy only supported with --csv\n')
            sys.exit(1)


    def run(self, args):
        self.setup_nova()
        self.setup_keystone()
        self.fetch_usage(args)
        headings = ["tenant_id", "tenant_name",
                    "instance_count", "instance_hours", "vcpu_hours",
                    "memory_hours_mb", "disk_hours_gb"]
        period = []
        if not args.legacy:
            headings = ["nu_year", "nu_month"] + headings
            period = [self.year, self.month]
        usage = map(lambda u: period + \
                    [u.tenant_id,
                     self.projects[u.tenant_id].name \
                     if u.tenant_id in self.projects else None,
                     len(u.server_usages),
                     u.total_hours,
                     u.total_vcpus_usage,
                     u.total_memory_mb_usage,
                     u.total_local_gb_usage],
                    self.raw_usage)
        
        if args.csv:
            self.csv_output(headings, usage, filename=args.filename)
        else:
            self.db_insert(headings, usage,
                           args.tablename or "nectar_usage",
                           replace={
                               'where': "nu_year = %s and nu_month = %s",
                               'params': [self.year, self.month]})
