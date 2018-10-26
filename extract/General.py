import sys
import os
import argparse
import re

from Subcommand import Processor

class General(Processor):
    def __init__(self):
        Processor.__init__(self)

    def build_parser(self, parent):
        parser = parent.add_parser(
            'general',
            help='extract general allocation information',
            epilog='Extracts general information about NeCTAR allocations \
            from the Allocations DB')
        parser.set_defaults(subcommand=lambda args: self.do_run(args))
        return parser

    def check_args(self, args):
        pass
        
    def run(self, args):
        self.setup_allocations()
        allocations = self.allocations.allocations.list()
        # print allocations 
        fields_to_report = [
            ("alloc_id", lambda x: x.id),
            ("tenant_id", lambda x: x.project_id),
            ("tenant_name", lambda x: x.project_name),
            ("project_name", lambda x: x.project_description),
            ("requested_allocation_home",
             lambda x: x.requested_allocation_home or ""),
            ("alloc_home",
             lambda x: x.allocation_home or ""),
            ("status", lambda x: x.status),
            ("submit_date", lambda x: x.submit_date),
            ("modified_time", lambda x: x.modified_time),
            ("instance_quota", lambda x: self._nova_quota(x, 'instances')),
            ("vcpu_quota", lambda x: self._nova_quota(x, 'cores')),
            ("ram_quota", lambda x: self._nova_quota(x, 'ram')),
            ("object_gb_quota",
             lambda x: self._zone_quota(x, 'object.object', 'nectar')),
            ("qriscloud_volume_gb_quota",
             lambda x: self._zone_quota(x, 'volume.gigabytes', 'QRIScloud')),
            ("qriscloud_rds_volume_gb_quota",
             lambda x: self._zone_quota(x, 'volume.gigabytes', 'QRIScloud-rds')),
            ("qriscloud_share_shares_quota",
             lambda x: self._zone_quota(x, 'share.shares', 'QRIScloud-GPFS')),
            ("qriscloud_share_snapshots_quota",
             lambda x: self._zone_quota(x, 'share.snapshots', 'QRIScloud-GPFS')),
            ("qriscloud_share_gb_quota",
             lambda x: self._zone_quota(x, 'share.gigabytes', 'QRIScloud-GPFS')),
            ("qriscloud_share_snapshot_gb_quota",
             lambda x: self._zone_quota(x, 'share.snapshot_gigabytes', 'QRIScloud-GPFS')),
            ("database_instance_quota",
             lambda x: self._zone_quota(x, 'database.instances', 'nectar')),
            ("database_volumes_quota",
             lambda x: self._zone_quota(x, 'database.volumes', 'nectar')),
            ("private_network_quota",
             lambda x: self._zone_quota(x, 'network.network', 'nectar')),
            ("floating_ip_quota",
             lambda x: self._zone_quota(x, 'network.floatingip', 'nectar')),
            ("router_quota",
             lambda x: self._zone_quota(x, 'network.router', 'nectar')),
            ("loadbalancer_quota",
             lambda x: self._zone_quota(x, 'network.loadbalancer', 'nectar')),
            ("for_1", lambda x: x.field_of_research_1),
            ("for_1_weight", lambda x: x.for_percentage_1),
            ("for_2", lambda x: x.field_of_research_2),
            ("for_2_weight", lambda x: x.for_percentage_2),
            ("for_3", lambda x: x.field_of_research_3),
            ("for_3_weight", lambda x: x.for_percentage_3),
            ("start_date", lambda x: x.start_date),
            ("end_date", lambda x: x.end_date),
            ("ncris_support", lambda x: x.ncris_support),            
            ("nectar_support", lambda x: x.nectar_support),
            ("contact_email", lambda x: x.contact_email),
            ("chief_investigator", lambda x: x.chief_investigator),
            ("estimated_project_duration",
             lambda x: x.estimated_project_duration),
            ("approver_email", lambda x: x.approver_email),
            ("estimated_number_users", lambda x: x.estimated_number_users),
            ("convert_trial_project", lambda x: x.convert_trial_project),
            ("provisioned", lambda x: x.provisioned),
            ("notifications", lambda x: x.notifications),
            ("parent_request", lambda x: x.parent_request)
        ]

        if args.csv:
            self.csv_output(map(lambda x: x[0], fields_to_report),
                            map(lambda alloc: map(
                                lambda y: y[1](alloc),
                                fields_to_report),
                                allocations),
                            filename=args.filename)
        else:
            self.db_insert(map(lambda x: x[0], fields_to_report),
                            map(lambda alloc: map(
                                lambda y: y[1](alloc),
                                fields_to_report),
                                allocations),
                           args.tablename or "nectar_general",
                           replaceAll=True)
    
    def _nova_quota(self, alloc, name):
        try:
            return alloc.get_allocated_nova_quota()[name]
        except KeyError:
            return 0

    def _zone_quota(self, alloc, resource, zone):
        try:
            st, rt = resource.split('.')
            for quota in alloc.get_quota(st):
                if quota.zone == zone and quota.resource == resource:
                    return quota.quota
            return 0
        except KeyError:
            return 0
        
