import sys
import os
import argparse
import datetime
import collections
import traceback

from Usages import Usages

class Instances(Usages):
    def __init__(self):
        Usages.__init__(self)

    @staticmethod
    def build_parser(parser, func):
        parser.epilog = 'Extracts NeCTAR instance usage from Nova'
        parser.add_argument('--qriscloud', action='store_true',
                            default=False,
                            help='Populate the "nectar_qriscloud_instances" table.')
        Usages.build_parser(parser, func)

    def check_args(self, args):
        Usages.check_args(self, args)
        
    def run(self, args):
        self.setup_nova()
        self.setup_keystone()
        self.fetch_usage(args)

        usage = []
        for u in self.raw_usage:
            tenant_id = u.tenant_id
            tenant_name = self.projects[tenant_id].name \
                          if tenant_id in self.projects else None

            # The Nova API doesn't allow "show" on deleted instances, but
            # we can get the info using "list --deleted".  The problem is
            # figuring out how to avoid retrieving irrelevant instances,
            # and at the same time how to avoid too many requests.
            #
            # Attempt #1 - use the tenant_id and the instance's name to
            # focus queries.
            # Attempt #2 - as #1, but after N lookups by name for a tenant,
            # just fetch all of the deleted instances.
            self.cache = {}
            try:
                for iu in u.server_usages:
                    name = iu['name']
                    instance_id = iu['instance_id']
                    instance = None
                    if iu['state'] == 'terminated' or iu['state'] == 'deleted':
                        instance = self.deleted(u.tenant_id,
                                                name, instance_id)
                    else:
                        try:
                            instance = self.nova.servers. \
                                       get(instance_id).to_dict()
                        except Exception:
                            if self.debug:
                                print('Cannot find instance {0} in {1}'
                                      .format(instance_id, u.tenant_id))
                    if instance is None:
                        az = 'unknown'
                    else:
                        az = instance['OS-EXT-AZ:availability_zone']
                    row = [tenant_id, tenant_name, instance_id, name,
                           iu['state'], iu['flavor'], iu['hours'],
                           iu['vcpus'], iu['memory_mb'], iu['local_gb'], az]
                    if args.qriscloud:
                        if az == 'QRIScloud':
                            usage.append([self.year, self.month] + row)
                    else:
                        usage.append(row)
            except Exception:
                traceback.print_exc(file=sys.stdout)

        headings = ["tenant_id", "tenant_name",
                    "instance_id", "instance_name",
                    "instance_state", "instance_flavour",
                    "instance_hours", "vcpus", "memory_mb",
                    "disk_gb", "az"]
        if args.qriscloud:
            headings = ['nu_year', 'nu_month'] + headings
        if args.csv:
            self.csv_output(headings, usage, filename=args.filename)
        elif args.qriscloud:
            self.db_insert(headings, usage,
                           args.tablename or "nectar_qriscloud_instances",
                           replace={
                               'where': "nu_year = %s and nu_month = %s",
                               'params': [self.year, self.month]})
        else:
            self.db_insert(headings, usage,
                           args.tablename or "nectar_instances",
                           replaceAll=True)


    def deleted(self, tenant_id, name, instance_id):
        # Since we need to use 'list' to retrieve info about deleted instances,
        # we keep a cache of the instances we have previously retrieved.
        # For the first few queries (< 4) we query by tenant_id & instance
        # name.  After that we do a query to fetch all deleted instances for
        # the tenant ...
        if name in self.cache:  # Lookup instances for name
            instances = cache[name]
        elif len(self.cache) < 4:  # Caching for a name
            try:
                instances = self.nova.servers.list(
                    detailed=True,
                    search_opts={'deleted': True,
                                 'all_tenants': True,
                                 'tenant_id': tenant_id,
                                 'name': name})
                if len(instances) == 0 and self.debug:
                    print("No deleted '{0}' instances in {1}".format(
                        name, tenant_id))
            except Exception:
                if self.debug:
                    print("Can't get deleted '{0}' instances in {1}".format(
                        name, tenant_id))
                    traceback.print_exc(file=sys.stdout)
                instances = []
            self.cache[name] = instances
        elif '*-*-ALL-*-*' in self.cache:  # Lookup the "all instances" name
            instances = self.cache['*-*-ALL-*-*']
        else:  # Cache "all instances"
            try:
                instances = self.nova.servers.list(
                    detailed=True,
                    search_opts={'deleted': True,
                                 'all_tenants': True,
                                 'tenant_id': tenant_id})
                if len(instances) == 0 and self.debug:
                    print("No deleted instances in {0}".format(tenant_id))
            except Exception:
                if self.debug:
                    print("Can't get deleted instances in {0}".format(
                        tenant_id))
                    traceback.print_exc(file=sys.stdout)
                instances = []
            self.cache['*-*-ALL-*-*'] = instances
        # Lookup the specific instance in the cached list of deleted instances
        try:
            return filter(
                lambda i: i.id == instance_id,
                instances)[0].to_dict()
        except Exception:
            if self.debug:
                print('Cannot find deleted instance {0} in {1}'.format(
                    instance_id, tenant_id))
        return None
