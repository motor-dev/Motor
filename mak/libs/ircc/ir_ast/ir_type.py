from .ir_object import IrObject
from .ir_declaration import IrDeclaration
from ..ir_codegen import IrccType
from ..ir_messages import IrAddressSpaceResolutionError
from motor_typing import TYPE_CHECKING
from abc import abstractmethod

_ADDRESS_SPACE_NAMES = ['private', 'global', 'constant', 'local']


class IrAddressSpace:
    # First unused generic address space
    GENERIC_ADDRESS_SPACE = 10

    def __init__(self, address_space):
        # type: (int) -> None
        if address_space == 4:
            address_space = IrAddressSpace.GENERIC_ADDRESS_SPACE
            IrAddressSpace.GENERIC_ADDRESS_SPACE += 1
        self._address_space = address_space

    def __str__(self):
        # type: () -> str
        try:
            return _ADDRESS_SPACE_NAMES[self._address_space]
        except IndexError:
            return 'generic'


class IrAddressSpaceInference:
    class AddressSpaceInformation:
        def __init__(self, address_space, location, type):
            # type: (int, IrPosition, IrType) -> None
            self._address_space = address_space
            self._location = location
            self._type = type
            self._deduced_from = None  # type: Optional[IrAddressSpaceInference.AddressSpaceInformation]

        def __hash__(self):
            # type: () -> int
            return self._address_space

        def __eq__(self, other):
            # type: (object) -> bool
            return isinstance(other, self.__class__) and self._address_space == other._address_space

        def __repr__(self):
            # type: () -> str
            return 'AddrSpace[%d]' % self._address_space

    def __init__(self):
        # type: () -> None
        self._calls = []           # type: List[IrAddressSpaceInference]
        self._address_spaces = {
        }                          # type: Dict[IrAddressSpaceInference.AddressSpaceInformation, List[IrAddressSpaceInference.AddressSpaceInformation]]

    def add(self, address_space, location, type, equivalent, equivalent_location, equivalent_type):
        # type: (IrAddressSpace, IrPosition, IrType, IrAddressSpace, IrPosition, IrType) -> None
        if address_space._address_space > 3:
            as_info = IrAddressSpaceInference.AddressSpaceInformation(address_space._address_space, location, type)
            eq = IrAddressSpaceInference.AddressSpaceInformation(
                equivalent._address_space, equivalent_location, equivalent_type
            )
            try:
                self._address_spaces[as_info].append(eq)
            except KeyError:
                self._address_spaces[as_info] = [eq]
        if equivalent._address_space > 3:
            as_info = IrAddressSpaceInference.AddressSpaceInformation(
                equivalent._address_space, equivalent_location, equivalent_type
            )
            eq = IrAddressSpaceInference.AddressSpaceInformation(address_space._address_space, location, type)
            try:
                self._address_spaces[as_info].append(eq)
            except KeyError:
                self._address_spaces[as_info] = [eq]

    def merge(self, other):
        # type: (IrAddressSpaceInference) -> None
        self._calls.append(other)

    def create_direct_map(self):
        # type: () -> Dict[int, int]
        result = {0: 0, 1: 1, 2: 2, 3: 3}
        calls_seen = set([])
        process = [self]

        inference = IrAddressSpaceInference()
        while process:
            call = process.pop(0)
            if call in calls_seen:
                continue
            calls_seen.add(call)
            for addr, eq_list in call._address_spaces.items():
                try:
                    inference._address_spaces[addr] += eq_list
                except KeyError:
                    inference._address_spaces[addr] = eq_list
            process += call._calls

        def _fill_bag(inference, address_space, equivalence_bag):
            # type: (IrAddressSpaceInference, IrAddressSpaceInference.AddressSpaceInformation, Dict[int, IrAddressSpaceInference.AddressSpaceInformation]) -> None
            for eq in inference._address_spaces[address_space]:
                if eq._address_space not in equivalence_bag:
                    eq._deduced_from = address_space
                    equivalence_bag[eq._address_space] = eq
                    if eq._address_space > 3:
                        _fill_bag(inference, eq, equivalence_bag)

        for address_space in inference._address_spaces.keys():
            if address_space._address_space not in result:
                equivalence_bag = {address_space._address_space: address_space}
                _fill_bag(inference, address_space, equivalence_bag)

                items = sorted(equivalence_bag.items())
                best_addr_space, best_info = items[0]
                if best_addr_space > 3:
                    raise IrAddressSpaceResolutionError(
                        address_space._location, str(address_space._type), 'unable to deduce address space'
                    )
                for addr_space, info in items[1:]:
                    if addr_space <= 3 and addr_space != best_addr_space:
                        second = IrAddressSpaceResolutionError(
                            info._location, str(info._type), _ADDRESS_SPACE_NAMES[addr_space]
                        )
                        first = IrAddressSpaceResolutionError(
                            best_info._location, str(best_info._type), _ADDRESS_SPACE_NAMES[best_addr_space], second
                        )
                        raise IrAddressSpaceResolutionError(
                            address_space._location, str(address_space._type),
                            "conflicting deduction of address space as '%s'" % _ADDRESS_SPACE_NAMES[addr_space], first
                        )
                    assert addr_space not in result
                    result[addr_space] = best_addr_space

        return result


class IrType(IrObject):
    def __init__(self):
        # type: () -> None
        IrObject.__init__(self)

    def resolve(self, module):
        # type: (IrModule) -> IrType
        return self

    def __str__(self):
        # type: () -> str
        raise NotImplementedError

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        raise NotImplementedError

    def _dependency_list(self):
        # type: () -> List[Tuple[str, IrDeclaration]]
        return []

    def flatten(self):
        # type: () -> List[IrType]
        return [self]

    def is_defined(self):
        # type: () -> bool
        return True

    def _get_target_type(self):
        # type: () -> IrType
        return self

    def extract(self, index):
        # type: (int) -> IrType
        raise NotImplementedError

    @abstractmethod
    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        raise NotImplementedError

    @abstractmethod
    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    @abstractmethod
    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    @abstractmethod
    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        raise NotImplementedError

    def add_equivalence_nonrecursive(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        pass

    def create_instance(self, equivalence):
        # type: (Dict[int, int]) -> None
        pass


class IrTypeDeclaration(IrDeclaration):
    TYPE_INDEX = 0

    def __init__(self, type):
        # type: (IrType) -> None
        IrDeclaration.__init__(self)
        self._type = type
        assert self._type._name is None
        self._type._name = 'type_%d' % IrTypeDeclaration.TYPE_INDEX
        self._current_index = 0
        IrTypeDeclaration.TYPE_INDEX += 1
        self._instances = {}   # type: Dict[str, Tuple[int, Dict[int, int]]]

    def resolve(self, module):
        # type: (IrModule) -> None
        self._type = self._type.resolve(module)

    def collect(self, ir_name):
        # type: (str) -> List[Tuple[str, IrDeclaration]]
        result = self._type._dependency_list()
        result.append((ir_name, self))
        return result

    def visit(self, generator, ir_name):
        # type: (IrccGenerator, str) -> None
        for signature, (index, equivalence) in self._instances.items():
            assert self._type._name is not None
            generator.declare_type(
                self._type.create_generator_type(generator, equivalence), '%s_%d' % (self._type._name, index), ir_name
            )

    def get_instance_name(self, equivalence):
        # type: (Dict[int, int]) -> str
        signature = self._type.signature(equivalence)
        return '%s_%d' % (self._type._name, self._instances[signature][0])

    def create_instance(self, equivalence):
        # type: (Dict[int, int]) -> None
        signature = self._type.signature(equivalence)
        if signature not in self._instances:
            self._instances[signature] = (self._current_index, equivalence)
            self._current_index += 1
            self._type.create_instance(equivalence)


class IrTypeReference(IrType):
    def __init__(self, reference):
        # type: (IrReference) -> None
        IrType.__init__(self)
        self._reference = reference
        self._declaration = None   # type: Optional[IrTypeDeclaration]
        self._target = None        # type: Optional[IrType]

    def resolve(self, module):
        # type: (IrModule) -> IrType
        self._declaration = module.get(self._reference, IrTypeDeclaration)
        self._target = self._declaration._type
        return self

    def extract(self, index):
        # type: (int) -> IrType
        assert self._target is not None
        return self._target.extract(index)

    def _get_target_type(self):
        # type: () -> IrType
        assert self._target is not None
        return self._target

    def _dependency_list(self):
        # type: () -> List[Tuple[str, IrDeclaration]]
        assert self._declaration is not None
        return self._declaration.collect(self._reference)

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        assert self._declaration is not None
        return generator.type_declared(self._declaration.get_instance_name(resolved_addressspace))

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        assert self._target is not None
        return self._target.create_generator_zero(generator, resolved_addressspace)

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        assert self._target is not None
        return self._target.create_generator_undef(generator, resolved_addressspace)

    def flatten(self):
        # type: () -> List[IrType]
        assert self._target is not None
        return self._target.flatten()

    def __str__(self):
        # type: () -> str
        return str(self._reference)

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        assert self._target is not None
        return self._target.signature(resolved_addressspace)

    def is_defined(self):
        # type: () -> bool
        assert self._target is not None
        return self._target.is_defined()

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        assert self._target is not None
        return self._target.add_equivalence(equivalence, location, other_type, other_location)

    def create_instance(self, equivalence):
        # type: (Dict[int, int]) -> None
        assert self._declaration is not None
        self._declaration.create_instance(equivalence)


class IrTypeOpaque(IrType):
    def __str__(self):
        # type: () -> str
        return 'opaque'

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '?'

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.type_void()

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        assert isinstance(other_type._get_target_type(), IrTypeOpaque)

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError


class IrTypeVoid(IrType):
    def __str__(self):
        # type: () -> str
        return 'void'

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '%'

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.type_void()

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        assert isinstance(other_type._get_target_type(), IrTypeVoid)

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError


class IrTypeUndef(IrType):
    def __str__(self):
        # type: () -> str
        return 'undef'

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '!'

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.type_undef()

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        assert isinstance(other_type._get_target_type(), IrTypeUndef)

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError


class IrTypeZero(IrType):
    def __str__(self):
        # type: () -> str
        return 'zero'

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '0'

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.type_zero()

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        assert isinstance(other_type._get_target_type(), IrTypeZero)

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError


class IrTypeMetadata(IrType):
    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.type_metadata()

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '~'

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        assert isinstance(other_type._get_target_type(), IrTypeMetadata)

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError


class IrTypeBuiltin(IrType):
    def __init__(self, builtin):
        # type: (str) -> None
        IrType.__init__(self)
        self._builtin = builtin

    def __str__(self):
        # type: () -> str
        return self._builtin

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '#%s' % self._builtin

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.type_builtin(self._builtin)

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        other_type = other_type._get_target_type()
        assert isinstance(other_type, IrTypeBuiltin)
        assert self._builtin == other_type._builtin

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_constant_zero()

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        assert self._builtin[0] == 'i'
        bitsize = min(8, int(self._builtin[1:]))
        return generator.make_expression_constant_undef(int(bitsize / 8))


class IrTypePtr(IrType):
    def __init__(self, pointee, addrspace):
        # type: (IrType, int) -> None
        IrType.__init__(self)
        self._pointee = pointee
        self._address_space = IrAddressSpace(addrspace)

    def resolve(self, module):
        # type: (IrModule) -> IrType
        self._pointee = self._pointee.resolve(module)
        return self

    def __str__(self):
        # type: () -> str
        return '%s %s*' % (self._pointee, self._address_space)

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '*[%d]%s' % (
            resolved_addressspace[self._address_space._address_space], self._pointee.signature(resolved_addressspace)
        )

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        addr_space = self._address_space._address_space
        if addr_space > 3:
            addr_space = resolved_addressspace[addr_space]
        return generator.make_ptr(
            generator.make_address_space(
                self._pointee.create_generator_type(generator, resolved_addressspace), addr_space
            )
        )

    def flatten(self):
        # type: () -> List[IrType]
        return [self]

    def is_defined(self):
        # type: () -> bool
        return self._address_space != 4 and self._pointee.is_defined()

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        other_type = other_type._get_target_type()
        assert isinstance(other_type, IrTypePtr)
        equivalence.add(self._address_space, location, self, other_type._address_space, other_location, other_type)
        self._pointee.add_equivalence(equivalence, location, other_type._pointee, other_location)

    def add_equivalence_nonrecursive(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        other_type = other_type._get_target_type()
        assert isinstance(other_type, IrTypePtr)
        equivalence.add(self._address_space, location, self, other_type._address_space, other_location, other_type)
        types = self._pointee.flatten()
        other_types = other_type._pointee.flatten()
        for t1, t2 in zip(types, other_types):
            t1.add_equivalence_nonrecursive(equivalence, location, t2, other_location)

    def create_instance(self, equivalence):
        # type: (Dict[int, int]) -> None
        self._pointee.create_instance(equivalence)

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_constant_zero()

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_constant_undef(4) # TODO


class IrTypeArray(IrType):
    def __init__(self, type, count):
        # type: (IrType, int) -> None
        IrType.__init__(self)
        self._type = type
        self._count = count

    def resolve(self, module):
        # type: (IrModule) -> IrType
        self._type = self._type.resolve(module)
        return self

    def _dependency_list(self):
        # type: () -> List[Tuple[str, IrDeclaration]]
        return self._type._dependency_list()

    def __str__(self):
        # type: () -> str
        return '%s[%d]' % (self._type, self._count)

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '[%d]%s' % (self._count, self._type.signature(resolved_addressspace))

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.make_array(self._type.create_generator_type(generator, resolved_addressspace), self._count)

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_array_value(
            [self._type.create_generator_zero(generator, resolved_addressspace)] * self._count
        )

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_array_value([])

    def flatten(self):
        # type: () -> List[IrType]
        return [self._type] * self._count

    def is_defined(self):
        # type: () -> bool
        return self._type.is_defined()

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        other_type = other_type._get_target_type()
        assert isinstance(other_type, IrTypeArray)
        assert self._count == other_type._count
        self._type.add_equivalence(equivalence, location, other_type._type, other_location)

    def create_instance(self, equivalence):
        # type: (Dict[int, int]) -> None
        self._type.create_instance(equivalence)


class IrTypeVector(IrType):
    def __init__(self, type, count):
        # type: (IrType, int) -> None
        IrType.__init__(self)
        self._type = type
        self._count = count

    def resolve(self, module):
        # type: (IrModule) -> IrType
        self._type = self._type.resolve(module)
        return self

    def _dependency_list(self):
        # type: () -> List[Tuple[str, IrDeclaration]]
        return self._type._dependency_list()

    def __str__(self):
        # type: () -> str
        return '%s%d' % (self._type, self._count)

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '<%d>%s' % (self._count, self._type.signature(resolved_addressspace))

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.make_vector(self._type.create_generator_type(generator, resolved_addressspace), self._count)

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_vector_value_broadcast(
            self.create_generator_type(generator, resolved_addressspace),
            self._type.create_generator_zero(generator, resolved_addressspace)
        )

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_vector_value_broadcast(
            self.create_generator_type(generator, resolved_addressspace),
            self._type.create_generator_undef(generator, resolved_addressspace)
        )

    def is_defined(self):
        # type: () -> bool
        return self._type.is_defined()

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        other_type = other_type._get_target_type()
        assert isinstance(other_type, IrTypeVector)
        assert self._count == other_type._count
        self._type.add_equivalence(equivalence, location, other_type._type, other_location)

    def create_instance(self, equivalence):
        # type: (Dict[int, int]) -> None
        self._type.create_instance(equivalence)


class IrTypeStruct(IrType):
    def __init__(self, fields, packed):
        # type: (List[IrType], bool) -> None
        IrType.__init__(self)
        self._fields = [(f, 'field_%d' % i) for i, f in enumerate(fields)]
        self._packed = packed

    def _dependency_list(self):
        # type: () -> List[Tuple[str, IrDeclaration]]
        result = []    # type: List[Tuple[str, IrDeclaration]]
        for t, _ in self._fields:
            result += t._dependency_list()
        return result

    def resolve(self, module):
        # type: (IrModule) -> IrType
        self._fields = [(f.resolve(module), n) for f, n in self._fields]
        return self

    def __str__(self):
        # type: () -> str
        return '{%s}' % (', '.join(str(x) for x, _ in self._fields))

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '{%s}' % (';'.join(x.signature(resolved_addressspace) for x, _ in self._fields))

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        return generator.make_struct(
            [(f.create_generator_type(generator, resolved_addressspace), n) for f, n in self._fields]
        )

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_aggregate_value(
            [t.create_generator_zero(generator, resolved_addressspace) for t, _ in self._fields]
        )

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        return generator.make_expression_aggregate_value(
            [t.create_generator_undef(generator, resolved_addressspace) for t, _ in self._fields]
        )

    def flatten(self):
        # type: () -> List[IrType]
        result = []    # type: List[IrType]
        for field in self._fields:
            result += field[0].flatten()
        return result

    def is_defined(self):
        # type: () -> bool
        result = True
        for t, _ in self._fields:
            result &= t.is_defined()
        return result

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        other_type = other_type._get_target_type()
        assert isinstance(other_type, IrTypeStruct)
        assert len(self._fields) == len(other_type._fields)
        for (t1, n1), (t2, n2) in zip(self._fields, other_type._fields):
            assert n1 == n2
            t1.add_equivalence(equivalence, location, t2, other_location)

    def extract(self, index):
        # type: (int) -> IrType
        assert index < len(self._fields)
        return self._fields[index][0]

    def create_instance(self, equivalence):
        # type: (Dict[int, int]) -> None
        for type, name in self._fields:
            type.create_instance(equivalence)


class IrTypeMethod(IrType):
    def __init__(self, return_type, argument_types):
        # type: (IrType, List[IrType]) -> None
        IrType.__init__(self)
        self._return_type = return_type
        self._argument_types = argument_types

    def _dependency_list(self):
        # type: () -> List[Tuple[str, IrDeclaration]]
        result = self._return_type._dependency_list()
        for t in self._argument_types:
            result += t._dependency_list()
        return result

    def resolve(self, module):
        # type: (IrModule) -> IrType
        self._return_type = self._return_type.resolve(module)
        self._argument_types = [t.resolve(module) for t in self._argument_types]
        return self

    def __str__(self):
        # type: () -> str
        return '%s(*)(%s)' % (self._return_type, ', '.join(str(x) for x in self._argument_types))

    def signature(self, resolved_addressspace):
        # type: (Dict[int, int]) -> str
        return '(%s(%s))' % (
            self._return_type.signature(resolved_addressspace),
            ';'.join(x.signature(resolved_addressspace) for x in self._argument_types)
        )

    def create_generator_type(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccType
        raise NotImplementedError

    def create_generator_zero(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    def create_generator_undef(self, generator, resolved_addressspace):
        # type: (IrccGenerator, Dict[int, int]) -> IrccExpression
        raise NotImplementedError

    def is_defined(self):
        # type: () -> bool
        result = self._return_type.is_defined()
        for t in self._argument_types:
            result &= t.is_defined()
        return result

    def add_equivalence(self, equivalence, location, other_type, other_location):
        # type: (IrAddressSpaceInference, IrPosition, IrType, IrPosition) -> None
        other_type = other_type._get_target_type()
        assert isinstance(other_type, IrTypeMethod)
        assert len(self._argument_types) == len(other_type._argument_types)
        self._return_type.add_equivalence(equivalence, location, other_type._return_type, other_location)
        for t1, t2 in zip(self._argument_types, other_type._argument_types):
            t1.add_equivalence(equivalence, location, t2, other_location)

    def create_instance(self, equivalence):
        # type: (Dict[int, int]) -> None
        self._return_type.create_instance(equivalence)
        for type in self._argument_types:
            type.create_instance(equivalence)


if TYPE_CHECKING:
    from typing import Dict, List, Optional, Set, Tuple
    from .ir_module import IrModule
    from .ir_reference import IrReference
    from ..ir_codegen import IrccGenerator, IrccType, IrccExpression
    from ..ir_position import IrPosition