import sys
import os
import argparse
import datetime
import collections

from Usages import Usages

class Instances(Usages):
    def __init__(self):
        Usages.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.epilog = 'Extracts NeCTAR instance usage from Nova'
        Usages.build_parser(parser, func)

    def check_args(self, args):
        Usages.check_args(self, args)
        
    def run(self, args):
        exit(1)
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

