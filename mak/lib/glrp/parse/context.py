from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union
from .production import Production
from .compound_symbol import CompoundSymbol, AmbiguousSymbol
from ..lex import Token

if TYPE_CHECKING:
    from .parse import MergeAction
    from ..symbol import Symbol


class ParseError(Exception):
    def __init__(self, recovery_operations: List[Union["RootOperation", "GoTo"]]) -> None:
        self._recovery_operations = recovery_operations


class SplitContext(object):
    __slots__ = ('_ref_count')

    def __init__(self, count: int) -> None:
        self._ref_count = count


class SplitInfo(object):
    __slots__ = ('_split', '_context', '_name', '_min_depth')

    def __init__(self, next: Optional["SplitInfo"], context: SplitContext, name: str, min_depth: int) -> None:
        self._split = next
        self._context = context
        self._name = name
        self._min_depth = min_depth

    def __del__(self) -> None:
        self._context._ref_count -= 1


class RootOperation(object):
    __slots__ = ('_state', '_split')

    def __init__(self, state: "State", split: Optional[SplitInfo]) -> None:
        self._state = state
        self._split = split

    def run(self) -> None:
        pass

    def run_debug(self) -> None:
        pass

    def recovery_operation(self) -> Union["RootOperation", "GoTo"]:
        return self


class InputToken(object):
    __slots__ = ('_state', '_predecessor', '_value', '_debug_value', '_split')

    def __init__(self, predecessor: Union[RootOperation, "Split", "GoTo"], token: Token) -> None:
        self._state = predecessor._state  # type: State
        self._predecessor = predecessor
        self._value = token
        self._debug_value = token  # type: Optional[Symbol]
        self._split = predecessor._split  # type: Optional[SplitInfo]

    def run(self) -> None:
        self._predecessor.run()

    def run_debug(self) -> None:
        self._predecessor.run_debug()


class Split(object):
    __slots__ = ('_state', '_predecessor', '_split')

    def __init__(
            self,
            predecessor: Union["GoTo", RootOperation],
            split_context: SplitContext,
            name: str,
            min_depth: int
    ) -> None:
        self._state = predecessor._state
        self._predecessor = predecessor
        self._split = SplitInfo(predecessor._split, split_context, name, min_depth)  # type: Optional[SplitInfo]

    def run(self) -> None:
        self._predecessor.run()

    def run_debug(self) -> None:
        self._predecessor.run_debug()

    def recovery_operation(self) -> Union[RootOperation, "GoTo"]:
        return self._predecessor


class Reduce(object):
    __slots__ = (
        '_state', '_predecessor', '_production_id', '_argument_count', '_callback', '_cached', '_value', '_debug_value',
        '_split'
    )

    def __init__(
            self,
            predecessor: Union[RootOperation, "GoTo", Split],
            production_id: int,
            argument_count: int,
            callback: Callable[..., Any]
    ) -> None:
        state = predecessor._state
        assert argument_count < state._depth
        for _ in range(0, argument_count):
            state = state._parent
        self._state = state
        self._predecessor = predecessor
        self._production_id = production_id
        self._argument_count = argument_count
        self._callback = callback
        self._cached = False
        self._value = None  # type: Any
        self._debug_value = None  # type: Optional[Symbol]
        self._split = predecessor._split  # type: Optional[SplitInfo]

    def run(self) -> None:
        if not self._cached:
            self._predecessor.run()
            try:
                self._value = self._callback(Production(self._predecessor._state, self._argument_count))
            except SyntaxError:
                raise ParseError([self._predecessor.recovery_operation()])
            self._cached = True

    def run_debug(self) -> None:
        if not self._cached:
            self._predecessor.run_debug()
            try:
                self._value = self._callback(Production(self._predecessor._state, self._argument_count))
            except SyntaxError:
                raise ParseError([self._predecessor.recovery_operation()])
            else:
                symbols = []  # type: List[Symbol]
                state = self._predecessor._state
                for i in range(0, self._argument_count):
                    assert state._debug_value is not None
                    symbols.append(state._debug_value)
                    state = state._parent
                self._debug_value = CompoundSymbol(self._production_id, (0, 0), symbols[::-1])
                self._cached = True

    def recovery_operation(self) -> Union[RootOperation, "GoTo"]:
        return self._predecessor.recovery_operation()


class GoTo(object):
    __slots__ = ('_state', '_predecessor', '_split')

    def __init__(self, predecessor: Union[Reduce, InputToken, "Merge"], new_state: int) -> None:
        self._state = State(predecessor._state, new_state)  # type: State
        self._predecessor = predecessor
        self._split = predecessor._split  # type: Optional[SplitInfo]

    def run(self) -> None:
        self._predecessor.run()
        self._state._value = self._predecessor._value

    def run_debug(self) -> None:
        self._predecessor.run_debug()
        assert self._predecessor._debug_value is not None
        self._state._value = self._predecessor._value
        self._state._debug_value = self._predecessor._debug_value

    def recovery_operation(self) -> Union[RootOperation, "GoTo"]:
        return self


class Merge(object):
    __slots__ = ('_state', '_predecessors', '_cached', '_value', '_debug_value', '_split', '_callback')

    def __init__(
            self,
            predecessor: Union[Reduce, "Merge"],
            split: SplitInfo,
            callback: "MergeAction.MergeCall"
    ) -> None:
        self._state = predecessor._state  # type: State
        self._predecessors = {split._name: [predecessor]}
        self._cached = False
        self._value = None  # type: Any
        self._debug_value = None  # type: Optional[Symbol]
        self._split = SplitInfo(split._split, split._context, callback._result,
                                split._min_depth)  # type: Optional[SplitInfo]
        split._context._ref_count += 1
        self._callback = callback

    def add_predecessor(self, predecessor: Union[Reduce, "Merge"], split: SplitInfo) -> None:
        try:
            self._predecessors[split._name].append(predecessor)
        except KeyError:
            self._predecessors[split._name] = [predecessor]

    def run(self) -> None:
        if not self._cached:
            self._cached = True
            recovery = []
            arg_count = 0
            prod_count = 0
            arguments = {}  # type: Dict[str, List[Any]]
            value = None  # type: Any
            for name, predecessors in self._predecessors.items():
                prod_count += 1
                values = []  # type: List[Any]
                arguments[name] = values
                for predecessor in predecessors:
                    try:
                        predecessor.run()
                    except ParseError as e:
                        recovery += e._recovery_operations
                    else:
                        value = predecessor._value
                        values.append(value)
                        arg_count += 1
            if arg_count == 0:
                raise ParseError(recovery)
            elif arg_count == 1:
                self._value = value
            else:
                self._value = self._callback(**arguments)

    def run_debug(self) -> None:
        if not self._cached:
            self._cached = True
            recovery = []
            arg_count = 0
            prod_count = 0
            arguments = {}
            value = None  # type: Any
            debug_values = []
            for name, predecessors in self._predecessors.items():
                prod_count += 1
                values = []  # type: List[Any]
                arguments[name] = values
                for predecessor in predecessors:
                    try:
                        predecessor.run_debug()
                    except ParseError as e:
                        recovery += e._recovery_operations
                    else:
                        value = predecessor._value
                        values.append(value)
                        debug_value = predecessor._debug_value
                        assert debug_value is not None
                        debug_values.append(debug_value)
                        arg_count += 1
            if arg_count == 0:
                raise ParseError(recovery)
            elif arg_count == 1:
                self._value = value
                self._debug_value = debug_value
            else:
                self._value = self._callback(**arguments)
                self._debug_value = AmbiguousSymbol(debug_values)


class State(object):
    __slots__ = ('_parent', '_state_id', '_value', '_debug_value', '_depth')

    def __init__(self, parent: Optional["State"], state_id: int) -> None:
        self._parent = parent or self
        self._state_id = state_id
        self._value = None  # type: Any
        self._debug_value = None  # type: Optional[Symbol]
        self._depth = (parent._depth + 1) if parent is not None else 1  # type: int
