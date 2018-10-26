import sys
import os
import argparse
import re
import collections

from Subcommand import Processor

class Homes(Processor):
    def __init__(self):
        Processor.__init__(self)

    def build_parser(self, parent):
        parser = parent.add_parser(
            'homes',
            help='extract allocation homes',
            epilog='Extracts NeCTAR project homes from Keystone')
        parser.add_argument('--legacy', action='store_true',
                            default=False,
                            help='Legacy (denormalized) table')
        parser.set_defaults(subcommand=lambda args: self.do_run(args))
        return parser

    def check_args(self, args):
        if not args.csv:
            # Currently, there is a table called 'nectar_qcif_overrides'
            # but it is populated manually and doesn't match what is in
            # the CSV file.
            sys.stderr.write('DB upload for "homes" not supported: use --csv\n')
            sys.exit(1)

    def run(self, args):
        separator = "," if args.csv else " "
        self.setup_keystone()
        all_users = map(lambda x: x.to_dict(),
                        self.keystone.users.list())
        inst_dict = {x['id']: x['email'].split("@")[-1] for x in all_users
                     if 'email' in x and x['email'] is not None}
        projects = self.keystone.projects.list()
        managers = collections.defaultdict(list)
        for user_role in self.keystone.role_assignments.list(role=14):
            if 'project' in user_role.scope:
                managers[user_role.scope['project']['id']].append(
                    user_role.user['id'])
        headings = ["tenant_id",
                    "allocation_homes" if args.legacy else "allocation_home"]
        records = []
        # If a project has an explicit allocation home recorded, use that.
        # Otherwise treat the institutions
        for proj in projects:
            if "allocation_home" in proj.to_dict():
                records.append([proj.id, proj.allocation_home])
            else:
                if len(managers[proj.id]) == 0:
                    continue
                institutions = set()
                for tm in managers[proj.id]:
                    if tm in inst_dict:
                        institutions.add(inst_dict[tm])
                if args.legacy:
                    records.append([proj.id,
                                    separator.join(institutions)])
                else:
                    for inst in institutions:
                        records.append([proj.id, inst])
        if args.csv:
            self.csv_output(headings, records, filename=args.filename)
        else:
            self.db_insert(headings, records,
                           args.tablename or "nectar_homes",
                           replaceAll=True)

