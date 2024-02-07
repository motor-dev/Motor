from .production import Production
from .compound_symbol import CompoundSymbol, AmbiguousSymbol
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple
from ..lex import Token
from ..symbol import Symbol

if TYPE_CHECKING:
    from .parse import MergeAction


class ParseError(Exception):

    def __init__(self, recovery_operation: "Operation") -> None:
        self.recovery_operation = recovery_operation


class SplitContext(object):
    __slots__ = ('_contexts', '_index')
    INDEX = 0

    def __init__(self) -> None:
        self._contexts = set()  # type: Set[Context]
        self._index = SplitContext.INDEX
        SplitContext.INDEX += 1

    def register(self, context: "Context") -> None:
        self._contexts.add(context)

    def unregister(self, context: "Context") -> None:
        self._contexts.remove(context)
        if len(self._contexts) == 1:
            context = self._contexts.pop()
            for i, st in enumerate(context._names):
                if st[0] == self:
                    context._names.pop(i)
                    break


SplitName = Tuple[SplitContext, str, int]


class Operation(object):
    __slots__ = ('_result_context', '_state', '_cache', '_cache_debug')

    def __init__(self, context: "Context", state: int):
        self._result_context = context
        self._state = state
        self._cache = None  # type: Optional[Tuple[Any]]
        self._cache_debug = None  # type: Optional[Tuple[Any, Symbol]]

    def undo(self, context: "Context", operation: "Operation") -> None:
        pass

    def run(self) -> Any:
        if self._cache is None:
            try:
                self._cache = (self._run(),)
            except SyntaxError:
                raise ParseError(self)
        return self._cache[0]

    def run_debug(self) -> Tuple[Any, Symbol]:
        if self._cache_debug is None:
            try:
                self._cache_debug = self._run_debug()
            except SyntaxError:
                raise ParseError(self)
        return self._cache_debug

    def _run(self) -> Any:
        raise NotImplementedError

    def _run_debug(self) -> Tuple[Any, Symbol]:
        raise NotImplementedError

    def goto(self, state: int) -> "Operation":
        return Goto(self, state)

    def consume_token(self, token: Token, state: int) -> "Operation":
        return ConsumeToken(self, token, state)

    def split(self, actions: Tuple[Tuple[int, Optional[str]], ...]) -> Tuple["Operation", ...]:
        if len(actions) > 1:
            split_context = SplitContext()
            result = tuple(Split(self, name or '_', split_context) for _, name in actions)
            self.discard()
            return result
        else:
            return (self,)

    def reduce(
            self, rule: Tuple[int, Tuple[int, ...], Callable[[Production], None], Dict[str, "MergeAction.MergeCall"]]
    ) -> "Operation":
        pop_count = len(rule[1])
        return Reduce(self, pop_count, self._state, rule)

    def discard(self) -> None:
        self._result_context._abandon()


class Reduce(Operation):
    __slots__ = ('_states', '_rule', '_predecessor')

    def __init__(self, origin, pop_count, state, rule):
        # type: (Operation, int, int, Tuple[int, Tuple[int, ...], Callable[[Production], None], Dict[str, MergeAction.MergeCall]]) -> None
        self._states = origin._result_context.pop(pop_count)
        Operation.__init__(self, origin._result_context, origin._result_context._state)
        self._rule = rule
        self._predecessor = origin

    def undo(self, context: "Context", operation: "Operation") -> None:
        if self._states:
            context._state_stack += self._states
            context._state = self._states[-1]
            context._sym_len += len(self._states)
        if operation != self:
            self._predecessor.undo(context, operation)

    def _run(self) -> Any:
        self._predecessor.run()
        pop_count = len(self._rule[1])
        while pop_count > len(self._result_context._prod_stack):
            self._result_context._merge_prod_parent()
        p = Production(self._result_context, pop_count)
        result = self._rule[2](p)
        self._result_context.reduce(pop_count)
        return result

    def _run_debug(self) -> Tuple[Any, Symbol]:
        self._predecessor.run_debug()
        pop_count = len(self._rule[1])
        while pop_count > len(self._result_context._prod_stack):
            self._result_context._merge_prod_parent()
        p = Production(self._result_context, pop_count)
        result = self._rule[2](p)
        if pop_count:
            debug_sym = CompoundSymbol(self._rule[0], (0, 0), self._result_context._debug_stack[-pop_count:])
        else:
            debug_sym = CompoundSymbol(self._rule[0], (0, 0), [])

        self._result_context.reduce_debug(pop_count)
        return (result, debug_sym)


class Goto(Operation):
    __slots__ = ('_predecessor', '_result_context')

    def __init__(self, origin: Operation, target_state: int) -> None:
        Operation.__init__(self, origin._result_context, target_state)
        self._predecessor = origin
        self._result_context.goto(target_state)

    def undo(self, context: "Context", operation: "Operation") -> None:
        context.pop(1)
        if operation != self:
            self._predecessor.undo(context, operation)

    def _run(self) -> Any:
        prod = self._predecessor.run()
        self._result_context.add_prod(prod)
        return None

    def _run_debug(self) -> Tuple[Any, Symbol]:
        prod, symbol = self._predecessor.run_debug()
        self._result_context.add_prod_debug(prod, symbol)
        return prod, symbol


class ConsumeToken(Operation):
    __slots__ = ('_predecessor', '_symbol', '_result_context')

    def __init__(self, origin: Operation, token: Token, target_state: int) -> None:
        Operation.__init__(self, origin._result_context, target_state)
        self._predecessor = origin
        self._symbol = token
        self._result_context.goto(target_state)

    def undo(self, context: "Context", operation: "Operation") -> None:
        context.pop(1)
        if operation != self:
            self._predecessor.undo(context, operation)

    def _run(self) -> Any:
        self._predecessor.run()
        self._result_context.add_prod(self._symbol)
        return None

    def _run_debug(self) -> Tuple[Any, Symbol]:
        self._predecessor.run_debug()
        self._result_context.add_prod_debug(self._symbol, self._symbol)
        return (None, self._symbol)


class Split(Operation):
    __slots__ = ('_predecessor')
    split_counter = 0

    def __init__(self, origin: Operation, name: str, split_context: SplitContext) -> None:
        Operation.__init__(
            self, Context(origin._result_context, (split_context, name, origin._result_context._sym_len)), origin._state
        )
        self._predecessor = origin

    def undo(self, context: "Context", operation: "Operation") -> None:
        if operation != self:
            self._predecessor.undo(context, operation)

    def _run(self) -> Any:
        return self._predecessor.run()

    def _run_debug(self) -> Tuple[Any, Symbol]:
        return self._predecessor.run_debug()


class Merge(Operation):
    __slots__ = ('_operations', '_original_operation', '_action', '_split_context', '_do_run')

    def __init__(
            self, operation: Operation, action: "MergeAction.MergeCall", name: str, split_context: SplitContext
    ) -> None:
        Operation.__init__(self, operation._result_context, operation._state)
        for i, st in enumerate(operation._result_context._names):
            if st[0] == split_context:
                operation._result_context._names[i] = (st[0], action._result, st[2])
                for st in operation._result_context._names[i + 1:]:
                    st[0].unregister(operation._result_context)
                operation._result_context._names = operation._result_context._names[0:i + 1]
                break
        self._operations = {name: [operation]}
        self._original_operation = operation
        self._action = action
        self._split_context = split_context
        self._do_run = False

    def undo(self, context: "Context", operation: "Operation") -> None:
        if operation != self:
            self._original_operation.undo(context, operation)

    def add_operation(self, operation: Operation, name: str, split_context: SplitContext) -> None:
        assert split_context == self._split_context
        # print('[%d] merge %s -> %s' % (split_context._index, name, self._action._result))
        # assert name == '_' or name not in self._operations
        self._do_run = True
        operation.discard()
        try:
            self._operations[name].append(operation)
        except KeyError:
            self._operations[name] = [operation]

    def _run(self) -> Any:
        if self._do_run:
            first_error = None  # type: Optional[ParseError]
            prod_count = 0
            values = dict(self._action._arguments)
            for key, operations in self._operations.items():
                prods = []  # type: List[Any]
                values[key] = prods
                for operation in operations:
                    try:
                        result = operation.run()
                    except ParseError as error:
                        if self._original_operation == operation:
                            first_error = error
                    else:
                        prods.append(result)
                        prod_count += 1
            if prod_count == 0:
                assert first_error is not None
                raise first_error
            elif prod_count > 1:
                result = self._action(**values)
        else:
            result = self._original_operation.run()

        return result

    def _run_debug(self) -> Tuple[Any, Symbol]:
        if self._do_run:
            first_error = None  # type: Optional[ParseError]
            prod_count = 0
            debug_symbols = []
            values = dict(self._action._arguments)
            for key, operations in self._operations.items():
                prods = []  # type: List[Any]
                values[key] = prods
                for operation in operations:
                    try:
                        result, debug_sym = operation.run_debug()
                    except ParseError as error:
                        if self._original_operation == operation:
                            first_error = error
                    else:
                        prods.append(result)
                        debug_symbols.append(debug_sym)
                        prod_count += 1
            if prod_count == 0:
                assert first_error is not None
                raise first_error
            elif prod_count > 1:
                result = self._action(**values)
                debug_sym = AmbiguousSymbol(debug_symbols)
        else:
            result, debug_sym = self._original_operation.run_debug()

        return result, debug_sym


class RootOperation(Operation):
    __slots__ = ('_token')

    def __init__(self, context: "Context", token: Token) -> None:
        Operation.__init__(self, context, context._state)
        self._token = token

    def undo(self, context: "Context", operation: "Operation") -> None:
        assert operation == self

    def _run(self) -> Any:
        return None

    def _run_debug(self) -> Tuple[Any, Symbol]:
        return (None, self._token)


class Context(object):
    __slots__ = ('_refcount', '_parent', '_prod_parent', '_state_stack', '_sym_len', '_state',
                 '_names', '_prod_stack', '_debug_stack')

    def __init__(self, parent: Optional["Context"], param_name: Optional[SplitName]) -> None:
        self._refcount = 1
        self._parent = parent
        self._prod_parent = parent
        if parent is not None:
            parent._refcount += 1
            self._state_stack = []  # type: List[int]
            self._sym_len = parent._sym_len  # type: int
            self._state = parent._state  # type: int
        else:
            self._state_stack = [0]
            self._sym_len = 0
            self._state = 0
        self._names = []  # type: List[SplitName]
        self._prod_stack = []  # type: List[Any]
        self._debug_stack = []  # type: List[Symbol]
        if param_name is not None:
            self._names.append(param_name)
            param_name[0].register(self)

    def _abandon(self) -> None:
        self._refcount -= 1
        if self._refcount == 0:
            for st in self._names:
                st[0].unregister(self)
            if self._parent is not None:
                self._parent._abandon()

    def _merge_parent(self) -> None:
        parent = self._parent
        assert parent is not None
        if parent._parent is not None:
            parent._parent._refcount += 1
        for st in parent._names:
            st[0].register(self)
        self._names = parent._names + self._names
        self._state_stack = parent._state_stack + self._state_stack
        self._parent = parent._parent
        parent._abandon()

    def _merge_prod_parent(self) -> None:
        parent = self._prod_parent
        assert parent is not None
        self._prod_stack = parent._prod_stack + self._prod_stack
        self._debug_stack = parent._debug_stack + self._debug_stack
        self._prod_parent = parent._prod_parent

    def flatten(self) -> "Context":
        result = Context(None, None)
        result._sym_len = self._sym_len
        result._state = self._state
        result._state_stack = self._state_stack
        result._prod_stack = self._prod_stack[:]
        result._debug_stack = self._debug_stack[:]
        p = self._parent
        while p is not None:
            result._state_stack = p._state_stack + result._state_stack
            p = p._parent
        p = self._prod_parent
        while p is not None:
            result._prod_stack = p._prod_stack + result._prod_stack
            result._debug_stack = p._debug_stack + result._debug_stack
            p = p._prod_parent
        return result

    def goto(self, state: int) -> None:
        self._sym_len += 1
        self._state = state
        self._state_stack.append(state)

    def add_prod(self, prod: Any) -> None:
        self._prod_stack.append(prod)

    def add_prod_debug(self, prod: Any, symbol: Symbol) -> None:
        self._prod_stack.append(prod)
        self._debug_stack.append(symbol)

    def pop(self, pop_count: int) -> List[int]:
        if pop_count != 0:
            while pop_count >= len(self._state_stack):
                self._merge_parent()
            self._sym_len -= pop_count
            result = self._state_stack[-pop_count:]
            del self._state_stack[-pop_count:]
            self._state = self._state_stack[-1]
            return result
        else:
            return []

    def reduce(self, pop_count: int) -> None:
        if pop_count != 0:
            del self._prod_stack[-pop_count:]

    def reduce_debug(self, pop_count: int) -> None:
        if pop_count != 0:
            del self._prod_stack[-pop_count:]
            del self._debug_stack[-pop_count:]

    def input(self, token: Token) -> Operation:
        return RootOperation(self, token)
