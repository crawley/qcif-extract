import sys
import os
import argparse
import re
import collections

from Subcommand import Processor

class Members(Processor):
    def __init__(self):
        Processor.__init__(self)

    def build_parser(self, parent):
        parser = parent.add_parser(
            'members',
            help='extract tenant members',
            epilog='Extracts NeCTAR project member email \
            addresses from Keystone')
        parser.set_defaults(subcommand=lambda args: self.do_run(args))
        return parser

    def check_args(self, args):
        pass
        
    def run(self, args):
        self.setup_keystone()
        all_users = map(lambda x: x.to_dict(),
                        self.keystone.users.list())
        email_dict = {x['id']: x['email'] for x in all_users
                      if 'email' in x and x['email'] is not None}
        projects = self.keystone.projects.list()
        members = collections.defaultdict(list)
        for user_role in self.keystone.role_assignments.list(role=2):
            if 'project' in user_role.scope:
                members[user_role.scope['project']['id']].append(
                    user_role.user['id'])
        headings = ["tenant_id", "tenant_member"]
        records = []
        separator = "," if args.csv else " "
        for proj in projects:
            if len(members[proj.id]) == 0:
                continue
            emails = set()
            for tm in members[proj.id]:
                if tm in email_dict:
                    emails.add(email_dict[tm])
            for email in emails:
                records.append([proj.id, email])
        if args.csv:
            self.csv_output(headings, records, filename=args.filename)
        else:
            self.db_insert(headings, records,
                           args.tablename or "nectar_tenant_members",
                           replaceAll=True)
