import sys
import os
import argparse
import datetime
import collections
import csv

from Nextcloud import Nextcloud

class NextcloudLogin(Nextcloud):
    def __init__(self):
        Nextcloud.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.epilog = 'Uploads Nextcloud login information'
        parser.add_argument('--after', default=None,
                            help='replaces data after the given date/time')
        Nextcloud.build_parser(parser, func)
        
    def check_args(self, args):
        Nextcloud.check_args(self, args)
        if args.after is not None:
            self.after = self.parseDateTime(args.after)
        else:
            self.after = None

    def parseDateTime(self, str):
        for f in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m"]:
            try:
                return datetime.datetime.strptime(str, f)
            except ValueError:
                pass
        raise ValueError

            
    def run(self, args):
        headings = ["account_name", "login_time_stamp"]
        raw_logins = self.load_file(args.input, fieldnames=headings)
        logins = map(lambda r: [r['account_name'],
                                self.parseDateTime(r['login_time_stamp'])],
                     raw_logins)
        print logins
        if self.after:
            logins = filter(lambda r: self.after < r[1], logins)
        if args.csv:
            self.csv_output(headings, logins, filename=args.filename)
        else:
            repl = None if self.after is None else {
                'where': "login_time_stamp > %s",
                'params': [self.after]}                      
            self.db_insert(headings, logins,
                           args.tablename or "nextcloud_logins",
                           replace=repl)
