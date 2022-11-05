from .production import Production
from .compound_symbol import CompoundSymbol, AmbiguousSymbol
from motor_typing import TYPE_CHECKING


class SplitContext(object):
    INDEX = 0

    def __init__(self):
        # type: () -> None
        self._contexts = set()     # type: Set[Context]
        self._index = SplitContext.INDEX
        SplitContext.INDEX += 1

    def register(self, context):
        # type: (Context) -> None
        self._contexts.add(context)

    def unregister(self, context):
        # type: (Context) -> None
        self._contexts.remove(context)
        if len(self._contexts) == 1:
            context = self._contexts.pop()
            for i, st in enumerate(context._names):
                if st[0] == self:
                    context._names.pop(i)
                    break


class Operation(object):

    def __init__(self, context, state):
        # type: (Context, int) -> None
        self._result_context = context
        self._state = state
        self._cache = None         # type: Optional[Tuple[Any]]
        self._cache_debug = None   # type: Optional[Tuple[Any, Symbol]]

    def run(self):
        # type: () -> Any
        if self._cache is None:
            self._cache = (self._run(), )
        return self._cache[0]

    def run_debug(self):
        # type: () -> Tuple[Any, Symbol]
        if self._cache_debug is None:
            self._cache_debug = self._run_debug()
        return self._cache_debug

    def _run(self):
        # type: () -> Any
        raise NotImplementedError

    def _run_debug(self):
        # type: () -> Tuple[Any, Symbol]
        raise NotImplementedError

    def goto(self, state):
        # type: (int) -> Operation
        return Goto(self, state)

    def consume_token(self, token, state):
        # type: (Token, int) -> Operation
        return ConsumeToken(self, token, state)

    def split(self, actions):
        # type: (Tuple[Tuple[int, Optional[str]],...]) -> Tuple[Operation,...]
        if len(actions) > 1:
            split_context = SplitContext()
            result = tuple(Split(self, name or '_', split_context) for _, name in actions)
            return result
        else:
            return (self, )

    def reduce(self, rule):
        # type: (Tuple[int, Tuple[int, ...], Callable[[Production], None], Dict[str, MergeAction.MergeCall]]) -> Operation
        pop_count = len(rule[1])
        return Reduce(self, pop_count, self._state, rule)

    def discard(self):
        # type: () -> None
        for st in self._result_context._names:
            st[0].unregister(self._result_context)


class Reduce(Operation):

    def __init__(self, origin, pop_count, state, rule):
        # type: (Operation, int, int, Tuple[int, Tuple[int, ...], Callable[[Production], None], Dict[str, MergeAction.MergeCall]]) -> None
        origin._result_context.pop(pop_count)
        Operation.__init__(self, origin._result_context, origin._result_context._state)
        self._rule = rule
        self._predecessor = origin

    def _run(self):
        # type: () -> Any
        self._predecessor.run()
        pop_count = len(self._rule[1])
        while pop_count > len(self._result_context._prod_stack):
            self._result_context._merge_prod_parent()
        p = Production(self._result_context, pop_count)
        result = self._rule[2](p)
        self._result_context.reduce(pop_count)
        return result

    def _run_debug(self):
        # type: () -> Tuple[Any, Symbol]
        self._predecessor.run_debug()
        pop_count = len(self._rule[1])
        while pop_count > len(self._result_context._prod_stack):
            self._result_context._merge_prod_parent()
        p = Production(self._result_context, pop_count)
        result = self._rule[2](p)
        if pop_count:
            debug_sym = CompoundSymbol(self._rule[0], 0, 0, self._result_context._debug_stack[-pop_count:])
        else:
            debug_sym = CompoundSymbol(self._rule[0], 0, 0, [])

        self._result_context.reduce_debug(pop_count)
        return (result, debug_sym)


class Goto(Operation):

    def __init__(self, origin, target_state):
        # type: (Operation, int) -> None
        if target_state == 249:
            pass
        Operation.__init__(self, origin._result_context, target_state)
        self._predecessor = origin
        self._result_context.goto(target_state)

    def _run(self):
        # type: () -> Any
        prod = self._predecessor.run()
        self._result_context.add_prod(prod)
        return None

    def _run_debug(self):
        # type: () -> Tuple[Any, Symbol]
        prod, symbol = self._predecessor.run_debug()
        self._result_context.add_prod_debug(prod, symbol)
        return prod, symbol


class ConsumeToken(Operation):

    def __init__(self, origin, token, target_state):
        # type: (Operation, Token, int) -> None
        Operation.__init__(self, origin._result_context, target_state)
        self._predecessor = origin
        self._symbol = token
        self._result_context.goto(target_state)

    def _run(self):
        # type: () -> Any
        self._predecessor.run()
        self._result_context.add_prod(self._symbol)
        return None

    def _run_debug(self):
        # type: () -> Tuple[Any, Symbol]
        self._predecessor.run_debug()
        self._result_context.add_prod_debug(self._symbol, self._symbol)
        return (None, self._symbol)


class Split(Operation):
    split_counter = 0

    def __init__(self, origin, name, split_context):
        # type: (Operation, str, SplitContext) -> None
        Operation.__init__(
            self, Context(origin._result_context, (split_context, name, origin._result_context._sym_len)), origin._state
        )
        self._predecessor = origin

    def _run(self):
        # type: () -> Any
        return self._predecessor.run()

    def _run_debug(self):
        # type: () -> Tuple[Any, Symbol]
        return self._predecessor.run_debug()


class Merge(Operation):

    def __init__(self, operation, action, name, split_context):
        # type: (Operation, MergeAction.MergeCall, str, SplitContext) -> None
        Operation.__init__(self, operation._result_context, operation._state)
        for i, st in enumerate(operation._result_context._names):
            if st[0] == split_context:
                operation._result_context._names[i] = (st[0], action._result, st[2])
                for st in operation._result_context._names[i + 1:]:
                    st[0].unregister(operation._result_context)
                operation._result_context._names = operation._result_context._names[0:i + 1]
                break
        self._operations = {name: [operation]}
        self._action = action
        self._split_context = split_context
        self._do_run = False

    def add_operation(self, operation, name, split_context):
        # type: (Operation, str, SplitContext) -> None
        assert split_context == self._split_context
        #print('[%d] merge %s -> %s' % (split_context._index, name, self._action._result))
        #assert name == '_' or name not in self._operations
        self._do_run = True
        operation.discard()
        try:
            self._operations[name].append(operation)
        except KeyError:
            self._operations[name] = [operation]

    def _run(self):
        # type: () -> Any
        if self._do_run:
            prod_count = 0
            values = dict(self._action._arguments)
            for key, operations in self._operations.items():
                prods = []     # type: List[Any]
                values[key] = prods
                for operation in operations:
                    try:
                        result = operation.run()
                    except SyntaxError:
                        pass
                    else:
                        prods.append(result)
                        prod_count += 1
            if prod_count == 0:
                raise SyntaxError
            elif prod_count > 1:
                result = self._action(**values)
        else:
            operations = self._operations.popitem()[1]
            result = operations[0].run()

        return result

    def _run_debug(self):
        # type: () -> Tuple[Any, Symbol]
        if self._do_run:
            prod_count = 0
            debug_symbols = []
            values = dict(self._action._arguments)
            for key, operations in self._operations.items():
                prods = []     # type: List[Any]
                values[key] = prods
                for operation in operations:
                    try:
                        result, debug_sym = operation.run_debug()
                    except SyntaxError:
                        pass
                    else:
                        prods.append(result)
                        debug_symbols.append(debug_sym)
                        prod_count += 1
            if prod_count == 0:
                raise SyntaxError
            elif prod_count > 1:
                result = self._action(**values)
                debug_sym = AmbiguousSymbol(debug_symbols)
        else:
            operations = self._operations.popitem()[1]
            result, debug_sym = operations[0].run_debug()

        return result, debug_sym


class RootOperation(Operation):

    def __init__(self, context, token):
        # type: (Context, Token) -> None
        Operation.__init__(self, context, context._state)
        self._token = token

    def _run(self):
        # type: () -> Any
        return None

    def _run_debug(self):
        # type: () -> Tuple[Any, Symbol]
        return (None, self._token)


class Context(object):

    def __init__(self, parent, param_name):
        # type: (Optional[Context], Optional[SplitName]) -> None
        self._refcount = 0
        self._parent = parent
        self._prod_parent = parent
        if parent is not None:
            parent._refcount += 1
            self._state_stack = []          # type: List[int]
            self._sym_len = parent._sym_len # type: int
            self._state = parent._state     # type: int
        else:
            self._state_stack = [0]
            self._sym_len = 0
            self._state = 0
        self._names = []                    # type: List[SplitName]
        self._prod_stack = []               # type: List[Any]
        self._debug_stack = []              # type: List[Symbol]
        if param_name is not None:
            self._names.append(param_name)
            param_name[0].register(self)

    def _abandon(self):
        # type: () -> None
        for st in self._names:
            st[0].unregister(self)

    def _merge_parent(self):
        # type: () -> None
        parent = self._parent
        assert parent is not None
        for st in parent._names:
            st[0].register(self)
        parent._refcount -= 1
        if parent._refcount == 0:
            parent._abandon()
        self._names = parent._names + self._names
        self._state_stack = parent._state_stack + self._state_stack
        self._parent = parent._parent

    def _merge_prod_parent(self):
        # type: () -> None
        parent = self._prod_parent
        assert parent is not None
        self._prod_stack = parent._prod_stack + self._prod_stack
        self._debug_stack = parent._debug_stack + self._debug_stack
        self._prod_parent = parent._prod_parent

    def goto(self, state):
        # type: (int) -> None
        self._sym_len += 1
        self._state = state
        self._state_stack.append(state)

    def add_prod(self, prod):
        # type: (Any) -> None
        self._prod_stack.append(prod)

    def add_prod_debug(self, prod, symbol):
        # type: (Any, Symbol) -> None
        self._prod_stack.append(prod)
        self._debug_stack.append(symbol)

    def pop(self, pop_count):
        # type: (int) -> None
        if pop_count != 0:
            while pop_count >= len(self._state_stack):
                self._merge_parent()
            self._sym_len -= pop_count
            del self._state_stack[-pop_count:]
            self._state = self._state_stack[-1]

    def reduce(self, pop_count):
        # type: (int) -> None
        if pop_count != 0:
            del self._prod_stack[-pop_count:]

    def reduce_debug(self, pop_count):
        # type: (int) -> None
        if pop_count != 0:
            del self._prod_stack[-pop_count:]
            del self._debug_stack[-pop_count:]

    def input(self, token):
        # type: (Token) -> Operation
        return RootOperation(self, token)


if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Set, Tuple
    SplitName = Tuple[SplitContext, str, int]
    from .parser import MergeAction
    from ..lex import Token
    from ..symbol import Symbol