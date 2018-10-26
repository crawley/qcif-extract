from Subcommand import Processor


class Projects(Processor):
    def __init__(self):
        Processor.__init__(self)

    def build_parser(self, parent):
        parser = parent.add_parser(
            'projects',
            help='extract projects',
            epilog='Extracts NeCTAR project data from Keystone')
        parser.set_defaults(subcommand=lambda args: self.do_run(args))
        return parser
        
    def check_args(self, args):
        pass

    def run(self, args):
        raise "not implemented yet!"
        self.setup_keystone()
        projects = self.keystone.projects.list()
        headings = ["tenant_id", "tenant_name", "description", "enabled",
                    "allocation_id", "expires"]
        info = map(lambda p: [p.tenant_id,
                              p.tenant_name,
                              p.description,
                              p.enabled,
                              p.allocation_id,
                              p.expires], projects)
        return
    
        if args.csv:
            self.csv_output(headings, usage, filename=args.filename)
        else:
            self.db_insert(headings, usage,
                           args.tablename or "nectar_usage",
                           replace={
                               'where': "nu_year = %s and nu_month = %s",
                               'params': [self.year, self.month]})
