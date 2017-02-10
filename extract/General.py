import sys
import os
import argparse
import re

from Subcommand import Processor

class General(Processor):
    def __init__(self):
        Processor.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.epilog = 'Blah'
        parser.set_defaults(subcommand=func)

    def check_args(self, args):
        pass
        
    def run(self, args):
        self.setup_allocations()
        allocations = self.allocations.get_allocations()
        fields_to_report = [
            ("tenant_id", lambda x: x['tenant_uuid']),
            ("tenant_name", lambda x: x['tenant_name']),
            ("project_name", lambda x: x['project_name']),
            ("alloc_home",
             lambda x: x['allocation_home'] if 'allocation_home' in x and
             x['allocation_home'] is not None else ""),
            ("status", lambda x: x['status']),
            ("modified_time", lambda x: x['modified_time']),
            ("instance_quota", lambda x: x['instance_quota']),
            ("vcpu_quota", lambda x: x['core_quota']),
            ("ram_quota", lambda x: x['ram_quota']),
            ("for_1", lambda x: x['field_of_research_1']),
            ("for_1_weight", lambda x: x['for_percentage_1']),
            ("for_2", lambda x: x['field_of_research_2']),
            ("for_2_weight", lambda x: x['for_percentage_2']),
            ("for_3", lambda x: x['field_of_research_3']),
            ("for_3_weight", lambda x: x['for_percentage_3']),
            ("start_date", lambda x: x['start_date']),
            ("end_date", lambda x: x['end_date']),
        ]

        if args.csv:
            self.csv_output(map(lambda x: x[0], fields_to_report),
                            map(lambda alloc: map(
                                lambda y: y[1](alloc),
                                fields_to_report),
                                allocations),
                            filename=args.filename)
        else:
            self.db_insert(map(lambda x: x[0], fields_to_report),
                            map(lambda alloc: map(
                                lambda y: y[1](alloc),
                                fields_to_report),
                                allocations),
                           args.tablename or "nectar_general",
                           replaceAll=True)
