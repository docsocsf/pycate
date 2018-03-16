class Exercise:
    def __init__(
            self, module_number, module_name, code, name, start, end,
            assessed_status, submission_status, links, spec_key):
        self.module_number = module_number
        self.module_name = module_name
        self.code = code
        self.name = name
        self.start = start
        self.end = end
        self.assessed_status = assessed_status
        self.submission_status = submission_status
        self.links = links
        self.spec_key = spec_key

    def __str__(self):
        return 'Exercise{{Module={} {};Code={};Name={}}}'.format(
            self.module_number,
            self.module_name,
            self.code,
            self.name
        )
