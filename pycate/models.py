class Exercise:
    def __init__(
            self, module_number, module_name, code, name, start, end,
            assessed_status, submission_status, links, spec_key):
        self.__module_number = module_number
        self.__module_name = module_name
        self.__code = code
        self.__name = name
        self.__start = start
        self.__end = end
        self.__assessed_status = assessed_status
        self.__submission_status = submission_status
        self.__links = links
        self.__spec_key = spec_key

    def __str__(self):
        return 'Exercise{{Module={} {};Code={};Name={}}}'.format(
            self.module_number,
            self.module_name,
            self.code,
            self.name
        )

    @property
    def module_number(self):
        return self.__module_number

    @property
    def module_name(self):
        return self.__module_name

    @property
    def code(self):
        return self.__code

    @property
    def name(self):
        return self.__name

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def assessed_status(self):
        return self.__assessed_status

    @property
    def submission_status(self):
        return self.__submission_status

    @property
    def links(self):
        return self.__links

    @property
    def spec_key(self):
        return self.__spec_key
