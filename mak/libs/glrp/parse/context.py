from .production import Production, AmbiguousProduction
from motor_typing import TYPE_CHECKING


class SplitContext(object):
    INDEX = 0

    def __init__(self, stack_unwind):
        # type: (int) -> None
        self._contexts = set()     # type: Set[Context]
        self._index = SplitContext.INDEX
        self._stack_unwind = stack_unwind
        SplitContext.INDEX += 1

    def register(self, context):
        # type: (Context) -> None
        self._contexts.add(context)

    def unregister(self, context):
        # type: (Context) -> None
        self._contexts.remove(context)
        if len(self._contexts) == 1:
            context = self._contexts.pop()
            for i, (sc, _) in enumerate(context._names):
                if sc == self:
                    context._names.pop(i)
                    break


class Operation(object):

    def __init__(self, tokens, context, pop_count, state, own_stack=[]):
        # type: (List[Token], Context, int, int, List[int]) -> None
        assert pop_count <= len(context._state_stack)
        self._tokens = tokens
        self._result_context = context
        self._pop_count = pop_count
        self._state = state
        self._own_stack = own_stack
        self._cache = None     # type: Optional[Tuple[Context, Optional[Symbol]]]
        self._sym_len = len(context._sym_stack) - pop_count + len(own_stack)

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

    def consume_token(self, state):
        # type: (int) -> Operation
        return ConsumeToken(self, state)

    def split(self, actions):
        # type: (Tuple[Tuple[int, Optional[str], Optional[str]],...]) -> Tuple[Operation,...]
        if len(actions) > 1:
            split_context = SplitContext(self._sym_len)
            result = tuple(Split(self, name or '_', split_context) for _, name, _ in actions)
            self.discard()
            return result
        else:
            return (self, )

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

    def discard(self):
        # type: () -> None
        for sc, _ in self._result_context._names:
            sc.unregister(self._result_context)


class Reduce(Operation):

    def __init__(self, origin, pop_count, state, own_stack, rule):
        # type: (Operation, int, int, List[int], Tuple[int, Tuple[int, ...], Callable[[Production], None], Dict[str, MergeAction.MergeCall]]) -> None
        Operation.__init__(self, origin._tokens, origin._result_context, pop_count, state, own_stack)
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
        if target_state == 249:
            pass
        Operation.__init__(
            self, origin._tokens, origin._result_context, origin._pop_count, target_state,
            origin._own_stack + [target_state]
        )
        self._predecessor = origin

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        context, symbol = self._predecessor.run()
        assert symbol is not None
        context.goto(self._state, symbol)
        return context, symbol


class ConsumeToken(Operation):

    def __init__(self, origin, target_state):
        # type: (Operation, int) -> None
        if target_state == 249:
            pass
        Operation.__init__(
            self, origin._tokens[1:], origin._result_context, origin._pop_count, target_state,
            origin._own_stack + [target_state]
        )
        self._predecessor = origin
        self._symbol = origin._tokens[0]

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        context, symbol = self._predecessor.run()
        context.goto(self._state, self._symbol)
        return context, self._symbol


class Split(Operation):
    split_counter = 0

    def __init__(self, origin, name, split_context):
        # type: (Operation, str, SplitContext) -> None
        Operation.__init__(
            self, origin._tokens, Context(origin._result_context, (split_context, name)), origin._pop_count,
            origin._state, origin._own_stack
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

    def __init__(self, operation, action, name, split_context):
        # type: (Operation, MergeAction.MergeCall, str, SplitContext) -> None
        context = Context(operation._result_context, None)
        operation.discard()
        for i, (sc, _) in enumerate(context._names):
            if sc == split_context:
                context._names[i] = (split_context, action._result)
                break
        Operation.__init__(
            self, operation._tokens, context, operation._pop_count, operation._state, operation._own_stack
        )
        self._operations = {name: [operation]}
        self._action = action
        self._split_context = split_context

    def add_operation(self, operation, name, split_context):
        # type: (Operation, str, SplitContext) -> None
        assert split_context == self._split_context
        #print('[%d] merge %s -> %s' % (split_context._index, name, self._action._result))
        #assert name == '_' or name not in self._operations
        operation.discard()
        try:
            self._operations[name].append(operation)
        except KeyError:
            self._operations[name] = [operation]

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        values = dict(self._action._arguments)
        prods = []
        for key, operations in self._operations.items():
            symbols = []   # type: List[Symbol]
            values[key] = symbols
            for operation in operations:
                context, symbol = operation.run()
                assert symbol is not None
                symbols.append(symbol)
                prods.append(symbol)
                           #print('[%d] %s -> %s' % (self._counter, ', '.join(self._operations.keys()), self._action._result))

        self._action(**values)
        self._result_context._state_stack = context._state_stack[:]
        self._result_context._sym_stack = context._sym_stack[:]
        self._result_context._state = context._state
        if len(prods) > 1:
            return self._result_context, AmbiguousProduction(prods)
        else:
            return self._result_context, prods[0]


class RootOperation(Operation):

    def __init__(self, context, tokens):
        # type: (Context, List[Token]) -> None
        Operation.__init__(self, tokens, context, 0, context._state)

    def _run(self):
        # type: () -> Tuple[Context, Optional[Symbol]]
        return self._result_context, None


class Context(object):

    class TokenCallback(object):

        def __init__(self):
            # type: () -> None
            pass

        def filter(self, context, token):
            # type: (Context, Token) -> List[Token]
            return [token]

    def __init__(self, parent, param_name):
        # type: (Optional[Context], Optional[Tuple[SplitContext, str]]) -> None
        if parent is not None:
            for sc, _ in parent._names:
                sc.register(self)
            self._state = parent._state                # type: int
            self._names = parent._names[:]             # type: List[Tuple[SplitContext, str]]
            self._state_stack = parent._state_stack[:] # type: List[int]
            self._sym_stack = parent._sym_stack[:]     # type: List[Symbol]
            self._filters = parent._filters[:]         # type: List[Context.TokenCallback]
        else:
            self._state = 0
            self._names = []
            self._state_stack = [0]
            self._sym_stack = []
            self._filters = [Context.TokenCallback()]
        if param_name is not None:
            self._names.append(param_name)
            param_name[0].register(self)

    def goto(self, state, symbol):
        # type: (int, Symbol) -> None
        self._state = state
        self._state_stack.append(state)
        self._sym_stack.append(symbol)

    def pop(self, pop_count):
        # type: (int) -> None
        self._state_stack = self._state_stack[:-pop_count]
        self._sym_stack = self._sym_stack[:-pop_count]

    def input(self, token):
        # type: (Token) -> Operation
        return RootOperation(self, self._filters[-1].filter(self, token))


if TYPE_CHECKING:
    from typing import Callable, Dict, List, Optional, Set, Tuple
    from .parser import MergeAction
    from ..lex import Token
    from ..symbol import Symbol