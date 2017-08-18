import sys
import os
import argparse
import datetime
import collections
import csv

from keystoneclient.exceptions import NotFound

from Subcommand import Processor

class Nextcloud(Processor):
    def __init__(self):
        Processor.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.add_argument('--input', metavar='FILENAME',
                            default=None,
                            help='Source file for Nextcloud data')
        parser.set_defaults(subcommand=func)

    def check_args(self, args):
        if not args.input:
            sys.stderr.write('The --input option is mandatory\n')
            sys.exit(1)

    def load_file(self, filename, fieldnames=None):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            return list(reader)
