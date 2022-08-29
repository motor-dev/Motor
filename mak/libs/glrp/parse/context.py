from .production import Production, AmbiguousProduction
from motor_typing import TYPE_CHECKING


class Operation(object):

    def __init__(self, context, pop_count, state, own_stack=[]):
        # type: (Context, int, int, List[int]) -> None
        assert pop_count <= len(context._state_stack)
        self._result_context = context
        self._pop_count = pop_count
        self._state = state
        self._own_stack = own_stack
        self._cache = None     # type: Optional[Tuple[Context, Optional[Symbol]]]

    def run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        if self._cache is not None:
            return self._cache
        else:
            self._cache = self._run()
            return self._cache

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        raise NotImplementedError

    def goto(self, state):
        # type: (int) -> Operation
        return Goto(self, state)

    def goto_token(self, state, token):
        # type: (int, Symbol) -> Operation
        return GotoToken(self, state, token)

    def split(self, name, split_counter):
        # type: (str, int) -> Operation
        return Split(self, name, split_counter)

    def reduce(self, rule):
        # type: (Tuple[int, Tuple[int, ...], Callable[[Production], None], Dict[str, MergeAction.MergeCall]]) -> Operation
        pop_count = len(rule[1])
        if pop_count == 0:
            return Reduce(self, self._pop_count, self._state, self._own_stack, rule)
        elif pop_count < len(self._own_stack):
            return Reduce(self, self._pop_count, self._own_stack[-pop_count - 1], self._own_stack[:-pop_count], rule)
        else:
            pop_count -= len(self._own_stack)
            return Reduce(
                self, self._pop_count + pop_count, self._result_context._state_stack[-pop_count - self._pop_count - 1],
                [], rule
            )


class Reduce(Operation):

    def __init__(self, origin, pop_count, state, own_stack, rule):
        # type: (Operation, int, int, List[int], Tuple[int, Tuple[int, ...], Callable[[Production], None], Dict[str, MergeAction.MergeCall]]) -> None
        Operation.__init__(self, origin._result_context, pop_count, state, own_stack)
        self._rule = rule
        self._predecessor = origin

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        context, symbol = self._predecessor.run()
        pop_count = len(self._rule[1])
        if pop_count == 0:
            p = Production(self._rule[0], 0, 0, [], self._rule[2])
        else:
            symbols = context._sym_stack[-pop_count:]
            p = Production(self._rule[0], 0, 0, symbols, self._rule[2])
            context.pop(pop_count)
        p.run()
        return context, p


class Goto(Operation):

    def __init__(self, origin, target_state):
        # type: (Operation, int) -> None
        Operation.__init__(
            self, origin._result_context, origin._pop_count, target_state, origin._own_stack + [target_state]
        )
        self._predecessor = origin

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        context, symbol = self._predecessor.run()
        assert symbol is not None
        context.goto(self._state, symbol)
        return context, symbol


class GotoToken(Operation):

    def __init__(self, origin, target_state, symbol):
        # type: (Operation, int, Symbol) -> None
        Operation.__init__(
            self, origin._result_context, origin._pop_count, target_state, origin._own_stack + [target_state]
        )
        self._predecessor = origin
        self._symbol = symbol

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        context, symbol = self._predecessor.run()
        context.goto(self._state, self._symbol)
        return context, self._symbol


class Split(Operation):
    split_counter = 0

    def __init__(self, origin, name, split_counter):
        # type: (Operation, str, int) -> None
        Operation.__init__(
            self, Context(origin._result_context, (name, split_counter)), origin._pop_count, origin._state,
            origin._own_stack
        )
        self._predecessor = origin
        self._name = name

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        context, symbol = self._predecessor.run()
        self._result_context._state_stack = context._state_stack[:]
        self._result_context._sym_stack = context._sym_stack[:]
        self._result_context._state = context._state
        return self._result_context, symbol


class Merge(Operation):

    def __init__(self, operation, action, name, split_counter):
        # type: (Operation, MergeAction.MergeCall, str, int) -> None
        context = Context(operation._result_context, None)
        context._parent = operation._result_context._parent
        context._names[split_counter] = action._result
        Operation.__init__(self, context, operation._pop_count, operation._state, operation._own_stack)
        self._operations = {name: operation}
        self._action = action
        self._name = name

    def add_operation(self, operation, name, split_counter):
        # type: (Operation, str, int) -> None
        self._operations[name] = operation

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        values = dict(self._action._arguments)
        prods = []
        for key, operation in self._operations.items():
            context, symbol = operation.run()
            assert symbol is not None
            values[key] = symbol
            prods.append(symbol)
        print('%s -> %s' % (', '.join(self._operations.keys()), self._action._result))
        self._action(**values)
        self._result_context._state_stack = context._state_stack[:]
        self._result_context._sym_stack = context._sym_stack[:]
        self._result_context._state = context._state
        return self._result_context, AmbiguousProduction(prods)


class RootOperation(Operation):

    def __init__(self, context):
        # type: (Context) -> None
        Operation.__init__(self, context, 0, context._state)

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        return self._result_context, None


class Context(object):

    def __init__(self, parent, param_name):
        # type: (Optional[Context], Optional[Tuple[str, int]]) -> None
        self._parent = parent
        if parent is not None:
            self._state = parent._state                # type: int
            self._names = dict(parent._names)          # type: Dict[int, str]
            self._state_stack = parent._state_stack[:] # type: List[int]
            self._sym_stack = parent._sym_stack[:]     # type: List[Symbol]
        else:
            self._state = 0
            self._names = dict()
            self._state_stack = [0]
            self._sym_stack = []
        if param_name is not None:
            assert param_name[1] not in self._names
            self._names[param_name[1]] = param_name[0]

    def goto(self, state, symbol):
        # type: (int, Symbol) -> None
        self._state = state
        self._state_stack.append(state)
        self._sym_stack.append(symbol)

    def pop(self, pop_count):
        # type: (int) -> None
        self._state_stack = self._state_stack[:-pop_count]
        self._sym_stack = self._sym_stack[:-pop_count]


if TYPE_CHECKING:
    from typing import Callable, Dict, List, Optional, Set, Tuple
    from .parser import MergeAction
    from ..symbol import Symbol