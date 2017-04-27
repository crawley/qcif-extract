import os
import sys
import logging

import ConfigParser
import csv

import mysql.connector
import os_client_config

from keystoneclient.exceptions import NotFound
from allocationsclient import Client as allocations_client


class Processor:
    def __init__(self):
        pass

    def do_run(self, args):
        self.check_args(args)

        self.debug = args.debug
        if self.debug:
            streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
            logging.basicConfig(level=logging.DEBUG,
                                format=streamformat)
            logging.getLogger('iso8601').setLevel(logging.WARNING)
            
        self.config = self.load_config(args.config)
        self.nova = None
        self.neutron = None
        self.keystone = None
        self.allocations = None

        if not args.csv:
            self.dryrun = args.dryrun
            self.db_username = self.config.get('DB', 'user')
            self.db_password = self.config.get('DB', 'password')
            self.db_host = self.config.get('DB', 'host')
            self.db_database = self.config.get('DB', 'database')
            assert self.db_database
    
        self.run(args);
        
    def check_args(self):
        pass

    def load_config(self, configPath):
        config = ConfigParser.SafeConfigParser({}, dict, True)
        config.readfp(open(os.path.expanduser(configPath), 'r'))
        return config

    def setup_nova(self):
        if not self.nova:
            self.nova = os_client_config.make_client('compute',
                                                     http_log_debug=self.debug)

    def setup_keystone(self):
        if not self.keystone:
            self.keystone = os_client_config.make_client('identity',
                                                         debug=self.debug)

    def setup_neutron(self):
        if not self.neutron:
            self.neutron = os_client_config.make_client('network',
                                                        http_log_debug=self.debug)

    def setup_allocations(self):
        if not self.allocations:
            self.allocations = allocations_client()
            
    def csv_output(self, headings, rows, filename=None):
        if filename is None:
            fp = sys.stdout
        else:
            fp = open(filename, 'wb')
        csv_output = csv.writer(fp, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
        csv_output.writerow(headings)
        for row in rows:
            csv_output.writerow(map(lambda x: unicode(x).encode('utf-8'), row))
        if filename is not None:
            fp.close()


    def db_insert(self, columns, rows, tablename, replaceAll=False):
        assert tablename
        if self.dryrun:
            print "DB host %s, User %s, Schema %s" % \
                (self.db_host, self.db_username, self.db_database)
        else:
            cnx = mysql.connector.connect(user=self.db_username,
                                          database=self.db_database,
                                          password=self.db_password,
                                          host=self.db_host)
            cursor = cnx.cursor()

        if replaceAll:
            delete_sql = "DELETE FROM %s" % (tablename)
            if self.dryrun:
                print delete_sql
            else:
                cursor.execute(delete_sql, [])
        
        insert_sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (
            tablename, ", ".join(columns),
            ", ".join(map(lambda x: "%s", columns)))
        if self.dryrun:
            print insert_sql
            
        for row in rows:
            if self.dryrun:
                print "row: %s" % (row)
            else:
                cursor.execute(insert_sql, row)

        if not self.dryrun:
            cnx.commit()
            cursor.close()
            cnx.close()
