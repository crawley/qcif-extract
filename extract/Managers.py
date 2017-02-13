import sys
import os
import argparse
import re
import collections

from Subcommand import Processor

class Managers(Processor):
    def __init__(self):
        Processor.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.epilog = 'Extracts NeCTAR project tenant manager email \
        addresses from Keystone'
        parser.add_argument('--legacy', action='store_true',
                            default=False,
                            help='Legacy (denormalized) table')
    
        parser.set_defaults(subcommand=func)

    def check_args(self, args):
        pass
        
    def run(self, args):
        self.setup_allocations()
        self.setup_keystone()
        allocations = self.allocations.get_allocations()
        all_users = map(lambda x: x.to_dict(),
                        self.keystone.users.list())
        email_dict = {x['id']: x['email'] for x in all_users
                      if 'email' in x and x['email'] is not None}
        projects = self.keystone.projects.list()
        managers = collections.defaultdict(list)
        for user_role in self.keystone.role_assignments.list(role=14):
            if 'project' in user_role.scope:
                managers[user_role.scope['project']['id']].append(
                    user_role.user['id'])
        headings = ["tenant_id",
                    "tenant_managers" if args.legacy else "tenant_manager"]
        records = []
        separator = "," if args.csv else " "
        for proj in projects:
            if len(managers[proj.id]) == 0:
                continue
            emails = set()
            for tm in managers[proj.id]:
                if tm in email_dict:
                    emails.add(email_dict[tm])
            if args.legacy:
                records.append([proj.id, separator.join(emails)])
            else:
                for email in emails:
                    records.append([proj.id, email])
        if args.csv:
            self.csv_output(headings, records, filename=args.filename)
        else:
            self.db_insert(headings, records,
                           args.tablename or "nectar_tenant_managers",
                           replaceAll=True)
