from . import types
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


class Template:
    class InstanciationError(Exception):
        def __init__(self, msg, position, error):
            self.msg = msg
            self.position = position
            self.error = error

    def __init__(self, position):
        self.parameters = []
        self.specializations = []
        self.created_instances = []
        self.name = None
        self.position = position
        self.specialization = False

    def get_token_type(self):
        return 'TEMPLATE_' + self.specializations[0][1].get_token_type()

    def find_nonrecursive(self, name):
        if self.name == name and not self.specialization:
            return self

    def add_template_parameter(self, parameter):
        self.parameters.append(parameter)

    def find(self, name, is_current_scope):
        for p in self.parameters:
            if p.name == name:
                return p

    def create_instance(self, arguments):
        specialization, template_arguments = self.find_specialization(arguments)
        instance = specialization.instantiate(template_arguments)
        self.created_instances.append((arguments, instance))
        return instance

    def instantiate(self, template_arguments):
        result = Template(self.position)
        result.name = self.name
        for p in self.parameters:
            result.add_template_parameter(p.instantiate(template_arguments))
        for params, s in self.specializations:
            instance_params = (p.instantiate(template_arguments) for p in params)
            instance_specialization = s.instantiate(template_arguments)
            result.specialize(tuple(instance_params), instance_specialization)
        return result

    def add(self, specialization):
        if not self.name:
            self.name = specialization.name
        self.specializations.append(([], specialization))

    def specialize(self, parameters, template_specialization):
        if not self.name:
            self.name = template_specialization.name
        self.specializations.append((parameters, template_specialization))

    def find_specialization(self, arguments):
        template_arguments = { }
        for parameter, argument in zip_longest(self.parameters, arguments):
            if not argument:
                raise Template.InstanciationError('too many template parameters')
            if not parameter:
                if not agument.default_value:
                    raise Template.InstanciationError('too few template parameters')
                else:
                    argument = parameter.default_value
            try:
                argument.is_valid(parameter)
            except AttributeError:
                raise Template.InstanciationError('Invalid value for template parameter %s' % parameter.name,
                                                  argument.position,
                                                  None)
            except types.ConversionError as e:
                if parameter.name:
                    raise Template.InstanciationError('Invalid value for template parameter %s' % parameter.name,
                                                      argument.position,
                                                      e)
                else:
                    raise Template.InstanciationError('Invalid value for template parameter',
                                                      argument.position,
                                                      e)
            if parameter.name:
                template_arguments[parameter.name] = { argument }
        return self.specializations[0][1], template_arguments

    def write_to(self, writer):
        for arguments, instance in self.created_instances:
            instance.write_to(writer)
