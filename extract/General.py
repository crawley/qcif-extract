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
        parser.epilog = 'Extracts general information about NeCTAR \
        allocations from the Allocations DB'
        parser.set_defaults(subcommand=func)

    def check_args(self, args):
        pass
        
    def run(self, args):
        self.setup_allocations()
        allocations = self.allocations.allocations.list()
        # print allocations 
        fields_to_report = [
            ("tenant_id", lambda x: x.project_id),
            ("tenant_name", lambda x: x.project_name),
            ("project_name", lambda x: x.project_description),
            ("alloc_home",
             lambda x: x.allocation_home or ""),
            ("status", lambda x: x.status),
            ("modified_time", lambda x: x.modified_time),
            ("instance_quota", lambda x: self._nova_quota(x, 'instances')),
            ("vcpu_quota", lambda x: self._nova_quota(x, 'cores')),
            ("ram_quota", lambda x: self._nova_quota(x, 'ram')),
            ("for_1", lambda x: x.field_of_research_1),
            ("for_1_weight", lambda x: x.for_percentage_1),
            ("for_2", lambda x: x.field_of_research_2),
            ("for_2_weight", lambda x: x.for_percentage_2),
            ("for_3", lambda x: x.field_of_research_3),
            ("for_3_weight", lambda x: x.for_percentage_3),
            ("start_date", lambda x: x.start_date),
            ("end_date", lambda x: x.end_date),
        ]

        # This deals with the fact that Mosaic only allows 16 bit values
        # for instance, vcpu and ram quotas.
        allocations = filter(lambda a: self._no_monster_quotas(a), allocations)

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
    
    def _no_monster_quotas(self, alloc):
        return self._nova_quota(alloc, 'instances') < 65536 and \
            self._nova_quota(alloc, 'cores') < 65536 and \
            self._nova_quota(alloc, 'ram') < 65536
    
    def _nova_quota(self, alloc, name):
        try:
            return alloc.get_allocated_nova_quota()[name]
        except KeyError:
            return 0
