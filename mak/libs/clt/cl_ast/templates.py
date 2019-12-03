from .cppobject import CppObject
from .error import CppError
from .scope import Scope
from .types import TypeRef, Type, BuiltIn, CastOptions, CastError
from .values import Constant


class TemplateValueParameter(CppObject):
    def __init__(self, lexer, position, name, type, value):
        CppObject.__init__(self, lexer, position, name)
        self.type = type
        self.value = value
        self.parameter_bind = None

    def __eq__(self, other):
        if not isinstance(other, TemplateTypenameParameter):
            return False
        if self.parameter_bind:
            return self.parameter_bind == other.parameter_bind
        else:
            return False

    def __hash__(self):
        return id(self)

    def get_unresolved_parameters(self):
        return [self]

    def get_parameter(self):
        return self.parameter_bind and self.parameter_bind[1] or self

    def is_bound(self):
        return self.parameter_bind != None

    def bind(self, argument_position, template):
        self.parameter_bind = (argument_position, template)

    def get_token_type(self):
        return 'VARIABLE_ID'

    def __str__(self):
        return '%s%s' % (self.type, self.name and ' '+self.name or '')

    def get_template_parameter_type(self):
        return self.type.name()

    def is_compatible(self, argument):
        return isinstance(argument, Constant)

    def template_parameter_match(self, value, cast_options):
        t = value.return_type()
        d = t.distance(self.type, CastOptions(CastOptions.CAST_IMPLICIT,
                                               cast_options.template_parameter_matches,
                                               cast_options.template_bindings,
                                               cast_options.current_template))
        d += Type.Distance(100000, matches={ self.parameter_bind[0]: value })
        return d

    def _create_template_instance(self, template, arguments, position):
        if template == self.parameter_bind[1]:
            return arguments[self.parameter_bind[0]]
        else:
            template_parent = self.lexer.scopes[-1].owner
            assert isinstance(template_parent, Template)
            value = self.value and self.value.create_template_instance(template, arguments, position)
            type = self.type.create_template_instance(template, arguments, position)
            result = TemplateValueParameter(self.lexer, position, self.name, type, value)
            result.bind(self.parameter_bind[0].create_template_instance(template, arguments, position), template_parent)
            return result


class TemplateTemplateParameter(CppObject):
    def __init__(self, lexer, position, name, template, value):
        CppObject.__init__(self, lexer, position, name)
        if len(template) > 1:
            raise SyntaxError
        self.template_params = template[0].parameters
        self.value = value
        self.parameter_bind = None

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        if self.parameter_bind:
            return self.parameter_bind == other.parameter_bind
        else:
            return False

    def get_unresolved_parameters(self):
        return [self]

    def get_parameter(self):
        return self.parameter_bind and self.parameter_bind[1] or self

    def is_bound(self):
        return self.parameter_bind != None

    def bind(self, argument_position, template):
        self.parameter_bind = (argument_position, template)

    def get_token_type(self):
        return 'TEMPLATE_TYPENAME_ID'

    def __str__(self):
        params = ', '.join(str(x) for x in self.template_params)
        return 'template<%s> typename%s' % (params, self.name and ' '+self.name or '')

    def get_template_parameter_type(self):
        return 'template typename'
    
    def is_compatible(self, argument):
        return (isinstance(argument, Template)
             or isinstance(argument, TemplateTemplateParameter)
             or (isinstance(argument, TypeRef) and argument.template_origin))

    def find_instance(self, template_on_stack, arguments, position):
        return None

    def instantiate(self, arguments, position):
        return None

    def distance(self, cast_to, cast_options):
        raise CastError('type %s is not compatible with %s' % (self, cast_to), self.position)

    def template_parameter_match(self, type, cast_options, typeref_from, typeref_typename):
        def _distance(parameters, value):
            if len(self.template_params) != len(parameters):
                raise CastError('type %s is not compatible with %s' % (typeref_from, typeref_typename), typeref_typename.position)
            d = Type.Distance(matches={self.parameter_bind[0]: value})
            for p1, p2 in zip(self.template_params, parameters):
                # d += p1.distance(p2, cast, matches, template_bindings)
                pass
            return d
        if isinstance(type, Template):
            return _distance(type.parameters, type)
        elif isinstance(type, TypeRef) and type.template_origin:
            return self.template_parameter_match(type.template_origin, cast_options, typeref_from, typeref_typename)
        elif isinstance(type, TemplateTemplateParameter):
            type_parameter_bind = type.parameter_bind or cast_options.template_bindings.get(type)
            if type_parameter_bind and type_parameter_bind == self.parameter_bind:
                return Type.Distance()
            elif type_parameter_bind and type_parameter_bind[1] == cast_options.current_template:
                return _distance(type.template_params, self)
            else:
                raise CastError('type %s is not compatible with %s' % (typeref_from, typeref_typename), typeref_typename.position)
        else:
            raise CastError('type %s is not compatible with %s' % (typeref_from, typeref_typename), typeref_typename.position)

    def _create_template_instance(self, template, arguments, position):
        if template == self.parameter_bind[1]:
            return arguments[self.parameter_bind[0]]
        else:
            template_parent = self.parameter_bind[1].create_template_instance(template, arguments, position)
            parameters = [p.create_template_instance(template, arguments, position) for p in self.template_params]
            value = self.value and self.value.create_template_instance(template, arguments, position)
            result = TemplateTemplateParameter(self.lexer, position, self.name, parameters, value)
            result.bind(self.parameter_bind[0], template_parent)
            return result


class TemplateTypenameParameter(Type):
    class INITIAL_SCOPE(Scope):
        def find(self, name, position, source_context, is_current_scope):
            return None

    def __init__(self, lexer, position, name, value):
        Type.__init__(self, lexer, position, name)
        self.value = value
        self.parameter_bind = None
        self.scope = lexer.UnknownScope()

    def __eq__(self, other):
        if not isinstance(other, TemplateTypenameParameter):
            return False
        if self.parameter_bind:
            return self.parameter_bind == other.parameter_bind
        else:
            return False

    def __hash__(self):
        return id(self)

    def get_unresolved_parameters(self):
        return [self]

    def get_parameter(self):
        return self.parameter_bind and self.parameter_bind[1] or self

    def is_bound(self):
        return self.parameter_bind != None

    def bind(self, argument_position, template):
        self.parameter_bind = (argument_position, template)

    def get_token_type(self):
        return 'TYPENAME_ID'

    def __str__(self):
        return 'typename%s' % (self.name and ' '+self.name or '')

    def get_template_parameter_type(self):
        return 'typename'
    
    def is_compatible(self, argument):
        return isinstance(argument, TypeRef)

    def signature(self):
        if self.parameter_bind:
            p = self.parameter_bind[1].scope.parameters[self.parameter_bind[0]]
        else:
            p = self
        return '<%s>'%p.name

    def template_parameter_match(self, type, cast_options, typeref_from, typeref_typename):
        def old_match():
            new_match = cast_options.template_parameter_matches[self.parameter_bind[0]].clone()
            for a in typeref_from.qualifiers:
                if a in new_match.qualifiers:
                    new_match.qualifiers.remove(a)
            return typeref_from.distance(new_match, CastOptions(CastOptions.CAST_NONE,
                                                                cast_options.template_parameter_matches,
                                                                cast_options.template_bindings,
                                                                cast_options.current_template))
        def make_match():
            match = typeref_from.clone()
            d = Type.Distance(variant=100000, matches={self.parameter_bind[0]: match})
            for a in typeref_typename.qualifiers:
                if a in typeref_from.qualifiers:
                    match.qualifiers.remove(a)
                    d = d.refine()
                elif cast_options.allowed_cast == cast_options.CAST_UNRELATED:
                    return Type.Distance(variant=-1)
                else:
                    raise CastError('type %s is not compatible with %s' % (typeref_from, typeref_typename), typeref_typename.position)
            #for a in typeref_from.qualifiers:
            #    if a not in typeref_typename.qualifiers:
            #        raise CastError('type %s is not compatible with %s' % (typeref_from, typeref_typename), self.position)
            return d
        if isinstance(type, TemplateTypenameParameter):
            type_parameter_bind = type.parameter_bind or cast_options.template_bindings.get(type)
            if self.parameter_bind == type_parameter_bind:
                return Type.Distance()
            elif self.parameter_bind and self.parameter_bind[1] == cast_options.current_template:
                if self.parameter_bind[0] in cast_options.template_parameter_matches:
                    return old_match()
                elif self.parameter_bind:
                    return make_match()
            elif cast_options.allowed_cast == cast_options.CAST_UNRELATED:
                return Type.Distance(variant=-1)
            else:
                raise CastError('type %s is not compatible with %s' % (typeref_from, typeref_typename), typeref_typename.position)
        elif self.parameter_bind and  self.parameter_bind[0] in cast_options.template_parameter_matches:
            return old_match()
        elif self.parameter_bind:
            return make_match()
        else:
            raise CastError('type %s is not compatible with %s' % (typeref_from, typeref_typename), typeref_typename.position)

    def _distance(self, cast_to, cast_options, typeref_from, typeref_to):
        raise CastError('type %s is not compatible with %s' % (typeref_from, typeref_to), self.position)

    def _create_template_instance(self, template, arguments, position):
        if template == self.parameter_bind[1]:
            return arguments[self.parameter_bind[0]]
        else:
            template_parent = self.parameter_bind[1].create_template_instance(template, arguments, position)
            value = self.value and self.value.create_template_instance(template, arguments, position)
            result = TemplateTypenameParameter(self.lexer, position, self.name, value)
            result.bind(self.parameter_bind[0], template_parent)
            return result


class TemplateScope(Scope):
    def __init__(self, owner, position):
        Scope.__init__(self, owner, position, scope_owner=owner.parent.scope.scope_owner)
        self.parameters = []

    def add(self, element):
        assert self.owner.back_link == self.owner
        if (isinstance(element, TemplateValueParameter)
         or isinstance(element, TemplateTemplateParameter)
         or isinstance(element, TemplateTypenameParameter)):
            self.parameters.append(element)
            self.owner.add_parameter(element)
        else:
            Scope.add(self, element)

    def find(self, name, position, source_context, is_current_scope):
        for element in self.parameters:
            result = element.find(name)
            if result:
                return result
        #else:
        #    if is_current_scope:
        #        return Scope.find(self.owner.back_link.scope, name, position, source_context, is_current_scope)
        #    else:
        #        return Scope.find(self, name, position, source_context, is_current_scope)


class Template(CppObject):
    class InstantiationError(CppError):
        pass

    def __init__(self, lexer, position):
        CppObject.__init__(self, lexer, position)
        self.back_link = self
        self.siblings = []
        self.parameters = []
        self.specializations = []
        self.push_scope(position, TemplateScope(self, position))
    
    def __eq__(self, other):
        if isinstance(other, Template):
            return id(self.back_link) == id(other.back_link)
        else:
            return False

    def __neq__(self, other):
        return not (self == other)

    def expand_template_arg_list(self, argument_list):
        if self != self.back_link:
            return self.back_link.expand_template_arg_list(argument_list)
        else:
            result = argument_list[:]
            for i in range(len(argument_list), len(self.parameters)):
                result.append(self.parameters[i].default_value)
            return result

    def add_parameter(self, parameter):
        if isinstance(parameter, TemplateTypenameParameter):
            self.parameters.append(TypeRef(self.lexer, parameter.position, parameter))
        else:
            self.parameters.append(parameter)

    def get_token_type_raw(self):
        if self.back_link == self:
            assert self.scope
            assert self.scope[0]
            return self.scope[0][1].get_token_type_raw()
        else:
            return self.back_link.get_token_type_raw()

    def get_token_type(self):
        if self.back_link == self:
            assert self.scope
            assert self.scope[0]
            return 'TEMPLATE_' + self.scope[0][1].get_token_type_raw()
        else:
            return self.back_link.get_token_type_raw()

    def bind(self, template):
        assert self.back_link == self or self.back_link == template
        if self.back_link == self:
            self.back_link = template
            template.siblings.append(self)
            if self.back_link != self:
                self.siblings.append(template)
            for i, p in enumerate(self.scope.parameters):
                p.bind(i, template)

    def find(self, name):
        if self.scope and self.scope.items:
            return self.scope[0][1].find(name) and self or None
        #elif self.back_link != self:
        #    return self.back_link.find(name)
        else:
            return None

    def distance(self, cast_to, cast_options):
        if isinstance(cast_to, TypeRef):
            other = other.template_origin
        if isinstance(cast_to, Template):
            if id(self) == id(cast_to):
                return Type.Distance()
            else:
                raise CastError('type %s is not compatible with %s' % (self, cast_to), self.position)
        elif isinstance(cast_to, TemplateTemplateParameter):
            params = other.template_params
        else:
            raise CastError('type %s is not compatible with %s' % (self, cast_to), self.position)
        if len(params) != len(self.scope.parameters):
            raise CastError('type %s is not compatible with %s' % (self, cast_to), self.position)
        d = Type.Distance()
        #for p1, p2 in zip(self.parameters, params):
        #    d += p1.distance(p2, cast)
        return d

    def instantiate(self, arguments, position):
        #self.lexer.note('creating instance of template %s'%self.scope[0][1].name, position)
        arguments = [a.simplify() for a in arguments]
        matches, specialization, scores = self.find_specialization(position, arguments)
        unresolved_params = []
        for a in arguments:
            unresolved_params += a.get_unresolved_parameters()
        if unresolved_params:
            for score in scores:
                if not score.exact_match():
                    return None
            else:
                return specialization
        specialization.push_scope_recursive(position)
        try:
            result = specialization.create_template_instance(self, matches, position)
        except Template.InstantiationError as e:
            specialization.pop_scope_recursive()
            args = ', '.join(str(a) for a in arguments)
            raise Template.InstantiationError('in instantiation of template %s<%s>'%(self.scope[0][1].pretty_name(), args), position, e)
        except:
            specialization.pop_scope_recursive()
            raise
        else:
            specialization.pop_scope_recursive()
            return result

    def fill_temporary_binding(self, template, binding):
        for i, p in enumerate(self.scope.parameters):
            binding[p] = (i, template)
        return binding

    def find_instance(self, template_bindings, arguments, position):
        arguments = self.match(arguments, position)
        assert len(arguments) == len(self.parameters)
        if template_bindings is not None:
            for i, p in enumerate(arguments):
                if not isinstance(p, TypeRef):
                    break
                if not (isinstance(p.type, TemplateTypenameParameter)
                     or isinstance(p.type, TemplateTemplateParameter)
                     or isinstance(p.type, TemplateValueParameter)):
                    break
                if p.qualifiers:
                    break
                if p.type.parameter_bind:
                    break
                if p.type not in template_bindings:
                    # definitely a dependent name
                    return None
                if template_bindings[p.type][0] != i:
                    break
                if template_bindings[p.type][1] != self:
                    break
            else:
                return self.scope[0][1]
            return self.find_exact_specialization(position, template_bindings, arguments)
        else:
            return self.instantiate(arguments, position)

    def _create_template_instance(self, template, arguments, position):
        assert self == self.back_link
        return Template(self.lexer, position)

    def _complete_template_instance(self, result, template, arguments, position):
        try:
            for p in self.scope.parameters:
                p = p.create_template_instance(template, arguments, position)
                result.scope.add(p)
            for s in self.siblings:
                for i, p in enumerate(s.scope.parameters):
                    p.create_template_instance(template, arguments, position).bind(i, result)
            if self.scope:
                if self.scope.empty():
                    # should not happen?
                    pass
                else:
                    result.scope.add(self.scope[0][1].create_template_instance(template, arguments, position))
            for specialization_parameters, specialization in self.specializations:
                params = [p.create_template_instance(template, arguments, position) for p in specialization_parameters]
                result.specializations.append((params, specialization.create_template_instance(template, arguments, position)))
        except Exception:
            self.lexer.pop_scope(result.scope)
            raise
        else:
            self.lexer.pop_scope(result.scope)
            return result

    def create_specialization(self, arguments, specialization):
        assert self == self.back_link
        self.specializations.append((arguments, specialization))

    def find_exact_specialization(self, position, template_bindings, arguments):
        for specialization_arguments, specialization in self.specializations:
            try:
                matches, scores = self.argument_match(specialization_arguments, arguments, template_bindings)
            except CastError:
                pass
            else:
                for score in scores:
                    if score == Type.Distance():
                        return None
                else:
                    return specialization

    def find_specialization(self, position, arguments):
        specializations = []
        for specialization_arguments, specialization in self.specializations:
            try:
                matches, score = self.argument_match(specialization_arguments, arguments, {})
            except CastError:
                pass
            else:
                specializations.append((score, matches, specialization))
        try:
            matches, score = self.argument_match(self.parameters, arguments, {})
        except CastError as e:
            raise Template.InstantiationError('when instantiating template', position, e)
        else:
            specializations.append((score, matches, self.scope[0][1]))
        if specializations:
            specializations = sorted(specializations, key=lambda x: x[0])
            score, matches, result = specializations[0]
            if len(specializations) > 1 and specializations[0][0] == specializations[1][0]:
                args = ', '.join(str(x) for x in arguments)
                self.lexer.error('ambiguous partial specializations of %s<%s>' % (self.scope[0][1].name, args),
                                 position)
                for s, m, r in specializations:
                    if s == score:
                        match_str = ', '.join('%s = %s' % (r.parent.scope.parameters[i].name or '<anonymous>', v) for i,v in sorted(m.items()))
                        self.lexer.note('partial specialization matches [%s]'%match_str, r.position)
                    else:
                        break
            return matches, result, score
        return None, None, None

    def get_unresolved_parameters(self):
        return []

    def argument_match(self, parameters, arguments, template_bindings):
        if len(arguments) != len(parameters):
            raise CastError('invalid number of parameters', self.position)
        matches = { }
        result = [ ]
        for a, p in zip(arguments, parameters):
            try:
                score = a.distance(p, CastOptions(CastOptions.CAST_NONE, matches, template_bindings, self))
            except CastError:
                a.distance(p, CastOptions(CastOptions.CAST_NONE, matches, template_bindings, self))
                raise CastError('template argument for template parameter %s is incompatible' % str(p), p.position)
            for k, v in score.matches.items():
                if k not in matches:
                    matches[k] = v
                else:
                    assert matches[k] == v
            result.append(score)
        return matches, result

    def debug_dump(self, indent=''):
        if self.scope and not self.scope.empty():
            params = ', '.join(str(p) for p in self.scope.parameters)
            print('%s%s<%s> [%s]' % (indent, self.__class__.__name__,
                                    params, self.position))
            self.scope[0][-1].debug_dump(indent)
            for args, pos, _, instance in self.scope[0][-1].instances:
                print('%s<%s> [%s]' % (indent, ', '.join('%d:%s'%(i,a) for i,a in sorted(args.items())), pos))
                instance.debug_dump(indent + '* ')
        for specialization_arguments, specialization in self.specializations:
            params = ', '.join(str(p) for p in specialization_arguments)
            print('%sspecialization: %s<%s> [%s]' % (indent, self.__class__.__name__,
                                        params, self.position))
            specialization.debug_dump(indent+' | ')
            for args, pos, _, instance in specialization.instances:
                print('%s<%s> [%s]' % (indent, ', '.join('%d:%s'%(i,a) for i,a in sorted(args.items())), pos))
                instance.debug_dump(indent + ' | * ')
            print(indent + ' `-- end specialization')

    def match(self, arguments, position):
        if len(arguments) > len(self.scope.parameters):
            raise self.InstantiationError('Too many template arguments',
                                          arguments[len(self.scope.parameters)].position)
        for missing_parameter in self.scope.parameters[len(arguments):]:
            if not missing_parameter.value:
                raise self.InstantiationError('too few template arguments', position)
            arguments.append(missing_parameter.value)
        for p, a in zip(self.scope.parameters, arguments):
            if not p.is_compatible(a):
                raise self.InstantiationError('Invalid template argument: expected %s, got %s' % (p.get_template_parameter_type(),
                                                                                                  a.__class__.__name__),
                                              a.position)
        return arguments

    def write_to(self, writer):
        if self.scope and not self.scope.empty():
            for _, _, _, instance in self.scope[0][-1].instances:
                instance.write_to(writer)
            for _, specialization in self.specializations:
                for _, _, _, instance in specialization.instances:
                    instance.write_to(writer)
