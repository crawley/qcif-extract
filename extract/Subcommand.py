import os
import sys
import logging

import ConfigParser
import csv

import mysql.connector

from keystoneclient.v3 import client as ks_client
from keystoneauth1.identity import v3 as ks_identity
from keystoneauth1 import session as ks_session
from keystoneclient.exceptions import NotFound
from novaclient import client as nova_client
from neutronclient.v2_0 import client as neutron_client
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
        self.username = os.environ.get('OS_USERNAME')
        self.password = os.environ.get('OS_PASSWORD')
        self.tenant = os.environ.get('OS_TENANT_NAME')
        self.url = os.environ.get('OS_AUTH_URL')
        self.region = os.environ.get('OS_REGION_NAME', None)
        self.auth = None
        self.session = None
        self.nova = None
        self.neutron = None
        self.keystone = None
        self.allocations = None

        if not args.csv:
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
            self.nova = nova_client.Client(2, self.username,
                                           self.password,
                                           self.tenant,
                                           self.url,
                                           service_type='compute',
                                           http_log_debug=self.debug)

    def setup_authsession(self):
        if not self.auth:
            self.auth = ks_identity.Password(username=self.username,
                                             password=self.password,
                                             project_name=self.tenant,
                                             user_domain_id="default",
                                             project_domain_id="default",
                                             auth_url=self.url)
            self.session = ks_session.Session(auth=self.auth)

    def setup_keystone(self):
        if not self.keystone:
            self.setup_authsession()
            self.keystone = ks_client.Client(session=self.session,
                                             debug=self.debug)

    def setup_neutron(self):
        if not self.neutron:
            self.setup_authsession()
            self.neutron = neutron_client.Client(session=self.session,
                                                 region_name=self.region,
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
        cnx = mysql.connector.connect(user=self.db_username, database=self.db_database,
                                      password=self.db_password, host=self.db_host)
        cursor = cnx.cursor()

        if replaceAll:
            delete_sql = "DELETE FROM %s" % (tablename)
            cursor.execute(delete_sql, [])
        
        insert_sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (
            tablename, ", ".join(columns), ", ".join(map(lambda x: "%s", columns)))
        for row in rows:
            cursor.execute(insert_sql, row)

        cnx.commit()
        cursor.close()
        cnx.close()
        
    
