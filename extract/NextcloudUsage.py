import sys
import os
import argparse
import datetime
import collections
import csv

from Nextcloud import Nextcloud

class NextcloudUsage(Nextcloud):
    def __init__(self):
        Nextcloud.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.epilog = 'Uploads Nextcloud usage information'
        Nextcloud.build_parser(parser, func)
        
    def check_args(self, args):
        Nextcloud.check_args(self, args)

    def run(self, args):
        headings = ["account_name", "quota", "consumed", "email"]
        raw_usage = self.load_file(args.input, fieldnames=headings)
        usage = map(lambda r: [r['account_name'], r['quota'],
                               r['consumed'], r['email']], raw_usage)
        if args.csv:
            self.csv_output(headings, usage, filename=args.filename)
        else:
            self.db_insert(headings, usage,
                           args.tablename or "nextcloud_usage",
                           replaceall=True)
