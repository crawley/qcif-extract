import sys
import os
import argparse
import re

from Subcommand import Processor

class Volumes(Processor):
    def __init__(self):
        Processor.__init__(self)

    def build_parser(self, parent):
        parser = parent.add_parser(
            'volumes',
            help='extract volume information',
            epilog='Extracts volume usage information from NeCTAR Cinder')
        parser.set_defaults(subcommand=lambda args: self.do_run(args))
        return parser

    def check_args(self, args):
        pass
        
    def run(self, args):
        self.setup_cinder()
        volumes = self.cinder.volumes.list(search_opts={'all_tenants': 1})
        fields_to_report = [
            ("volume_id", lambda x: x.id),
            ("tenant_id",
             lambda x: getattr(x, 'os-vol-tenant-attr:tenant_id')),
            ("availability_zone", lambda x: x.availability_zone),
            ("volume_type", lambda x: x.volume_type),
            ("name", lambda x: x.name),
            ("size", lambda x: x.size),
            ("created_at", lambda x: x.created_at),
            ("status", lambda x: x.status)
        ]

        if args.csv:
            self.csv_output(map(lambda x: x[0], fields_to_report),
                            map(lambda alloc: map(
                                lambda y: y[1](alloc),
                                fields_to_report),
                                volumes),
                            filename=args.filename)
        else:
            self.db_insert(map(lambda x: x[0], fields_to_report),
                            map(lambda alloc: map(
                                lambda y: y[1](alloc),
                                fields_to_report),
                                volumes),
                           args.tablename or "nectar_volumes",
                           replaceAll=True)
    
