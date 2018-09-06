import os
import sys
import logging

import ConfigParser
import csv

import mysql.connector
from os_client_config import make_client 

from keystoneclient.exceptions import NotFound

from keystoneauth1 import loading, session
from nectarallocationclient import client

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
            self.nova = make_client('compute',
                                    http_log_debug=self.debug)

    def setup_keystone(self):
        if not self.keystone:
            self.keystone = make_client('identity',
                                        debug=self.debug)

    def setup_neutron(self):
        if not self.neutron:
            self.neutron = make_client('network',
                                       http_log_debug=self.debug)

    def setup_allocations(self):
        if not self.allocations:
            loader = loading.get_plugin_loader('password')
            username = os.environ.get('OS_USERNAME')
            password = os.environ.get('OS_PASSWORD')
            auth_url = os.environ.get('OS_AUTH_URL')
            project_name = os.environ.get('OS_TENANT_NAME')
            auth = loader.load_from_options(auth_url=auth_url,
                                            username=username,
                                            password=password,
                                            project_name=project_name,
                                            user_domain_id='default',
                                            project_domain_id='default')
            sess = session.Session(auth=auth)
            self.allocations = client.Client(1, session=sess)
            
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

    def db_insert(self, columns, rows, tablename,
                  replaceAll=False, replace=None):
        assert tablename
        assert not replaceAll or replace is None
        if replaceAll:
            delete_sql = "DELETE FROM %s" % (tablename)
            delete_params = [[]]
        elif replace is not None:
            delete_sql = "DELETE FROM %s WHERE %s" % (
                tablename, replace['where'])
            delete_params = [replace['params']]
        else:
            delete_sql = delete_params = None
            
        insert_sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (
            tablename, ", ".join(columns),
            ", ".join(map(lambda x: "%s", columns)))
        self._db_transaction(delete_sql, delete_params, insert_sql, rows)  

    def _db_transaction(self, prep_sql, prep_params, insert_sql, insert_rows):
        if self.dryrun:
            print "DB host %s, User %s, Schema %s" % \
                (self.db_host, self.db_username, self.db_database)
            cursor = None
        else:
            cnx = mysql.connector.connect(user=self.db_username,
                                          database=self.db_database,
                                          password=self.db_password,
                                          host=self.db_host)
            cursor = cnx.cursor()

        if prep_sql:
            self._db_execute(cursor, prep_sql, prep_params)
        self._db_execute(cursor, insert_sql, insert_rows)

        if not self.dryrun:
            cnx.commit()
            cursor.close()
            cnx.close()
            
    def _db_execute(self, cursor, sql, param_sets):
        if self.dryrun:
            print "sql: %s" % (sql)
            
        for params in param_sets:
            if self.dryrun:
                print "params: %s" % (params)
            else:
                try:
                    cursor.execute(sql, params)
                except Exception:
                    t, v, tb = sys.exc_info()
                    print "sql: %s" % (sql)
                    print "params: %s" % (params)
                    raise t, v, tb

