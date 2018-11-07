import sys
import os
import argparse
import re

from Subcommand import Processor

class Grants(Processor):
    def __init__(self):
        Processor.__init__(self)

    def build_parser(self, parent):
        parser = parent.add_parser(
            'grants',
            help='extract allocation grant information',
            epilog='Extracts information about NeCTAR allocations supporting \
            grants from the Allocations DB')
        parser.set_defaults(subcommand=lambda args: self.do_run(args))
        return parser

    def check_args(self, args):
        pass
        
    def run(self, args):
        self.setup_allocations()
        grants = self.allocations.grants.list()
        fields_to_report = [
            ("id", lambda x: x.id),
            ("alloc_id", lambda x: x.allocation),
            ("grant_type", lambda x: x.grant_type),
            ("funding_body_scheme", lambda x: x.funding_body_scheme),
            ("grant_id", lambda x: x.grant_id),
            ("first_year_funded", lambda x: x.first_year_funded),
            ("last_year_funded", lambda x: x.last_year_funded),
            ("total_funding", lambda x: x.total_funding),
        ]

        if args.csv:
            self.csv_output(map(lambda x: x[0], fields_to_report),
                            map(lambda alloc: map(
                                lambda y: y[1](alloc),
                                fields_to_report),
                                grants),
                            filename=args.filename)
        else:
            self.db_insert(map(lambda x: x[0], fields_to_report),
                            map(lambda alloc: map(
                                lambda y: y[1](alloc),
                                fields_to_report),
                                grants),
                           args.tablename or "nectar_grants",
                           replaceAll=True)
