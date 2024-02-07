from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union
from ..lex import Token

if TYPE_CHECKING:
    from .parse import MergeAction


class ParseError(Exception):
    def __init__(self, recovery_operations: List[Union["RootOperation", "GoTo"]]) -> None:
        self._recovery_operations = recovery_operations


class SplitContext(object):
    __slots__ = ('_ref_count')

    def __init__(self, count: int) -> None:
        self._ref_count = count


class SplitInfo(object):
    __slots__ = ('_split', '_context', '_name', '_min_depth')

    def __init__(self, next: Optional["SplitInfo"], context: SplitContext, name: Optional[str], min_depth: int) -> None:
        self._split = next
        self._context = context
        self._name = name
        self._min_depth = min_depth

    def __del__(self) -> None:
        self._context._ref_count -= 1


class Production(object):
    __slots__ = ('_state', '_length')

    def __init__(self, state: "State", prod_len: int) -> None:
        self._state = state
        self._length = prod_len

    def __len__(self):
        # type: () -> int
        return self._length

    def __getitem__(self, index):
        # type: (int) -> Any
        state = self._state
        index += 1
        while index < self._length:
            state = state._parent
            index += 1
        return state._value


class RootOperation(object):
    __slots__ = ('_state', '_split')

    def __init__(self, state: "State", split: Optional[SplitInfo]) -> None:
        self._state = state
        self._split = split

    def run(self) -> None:
        pass


class InputToken(object):
    __slots__ = ('_state', '_predecessor', '_value', '_split')

    def __init__(self, predecessor: Union[RootOperation, "GoTo"], token: Token) -> None:
        self._state = predecessor._state  # type: State
        self._predecessor = predecessor
        self._value = token
        self._split = predecessor._split  # type: Optional[SplitInfo]

    def run(self) -> None:
        self._predecessor.run()

    def recovery_operation(self) -> Union["GoTo", "InputToken"]:
        return self


class Split(object):
    __slots__ = ('_state', '_predecessor', '_split')

    def __init__(
            self,
            predecessor: Union["GoTo", InputToken],
            split_context: SplitContext,
            name: Optional[str],
            min_depth: int
    ) -> None:
        self._state = predecessor._state
        self._predecessor = predecessor
        self._split = SplitInfo(predecessor._split, split_context, name, min_depth)

    def run(self) -> None:
        self._predecessor.run()

    def recovery_operation(self) -> Union["GoTo", InputToken]:
        return self._predecessor


class Reduce(object):
    __slots__ = (
        '_state', '_predecessor', '_argument_count', '_callback', '_cached', '_value', '_split'
    )

    def __init__(
            self,
            predecessor: Union["GoTo", Split, InputToken],
            argument_count: int,
            callback: Callable[..., Any]
    ) -> None:
        state = predecessor._state
        assert argument_count < state._depth
        for _ in range(0, argument_count):
            state = state._parent
        self._state = state
        self._predecessor = predecessor
        self._argument_count = argument_count
        self._callback = callback
        self._cached = False
        self._value = None  # type: Any
        self._split = predecessor._split  # type: Optional[SplitInfo]

    def run(self) -> None:
        if not self._cached:
            self._predecessor.run()
            try:
                self._value = self._callback(Production(self._predecessor._state, self._argument_count))
            except SyntaxError:
                raise ParseError([self._predecessor.recovery_operation()])
            self._cached = True

    def recovery_operation(self) -> Union["GoTo", InputToken]:
        return self._predecessor.recovery_operation()


class GoTo(object):
    __slots__ = ('_state', '_predecessor', '_split')

    def __init__(self, predecessor: Union[Reduce, Split, InputToken, "Merge"], new_state: int) -> None:
        self._state = State(predecessor._state, new_state)  # type: State
        self._predecessor = predecessor
        self._split = predecessor._split  # type: Optional[SplitInfo]

    def run(self) -> None:
        self._predecessor.run()
        self._state._value = self._predecessor._value

    def recovery_operation(self) -> Union["GoTo", InputToken]:
        return self


class Merge(object):
    __slots__ = ('_state', '_predecessors', '_cached', '_value', '_split', '_callback')

    def __init__(
            self,
            predecessor: Union[Reduce, "Merge"],
            split: SplitInfo,
            callback: "MergeAction.MergeCall"
    ) -> None:
        self._state = predecessor._state
        self._predecessors = {split._name: [predecessor]}
        self._cached = False
        self._value = None  # type: Any
        self._split = SplitInfo(split._split, split._context, callback._result, split._min_depth)
        split._context._ref_count += 1
        self._callback = callback

    def add_predecessor(self, predecessor: Union[Reduce, "Merge"], split: SplitInfo):
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
            arguments = {}
            value = None  # type: Any
            for name, predecessors in self._predecessors.items():
                prod_count += 1
                values = []
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


class State(object):
    __slots__ = ('_parent', '_state_id', '_value', '_dbg_value', '_depth')

    def __init__(self, parent: Optional["State"], state_id: int) -> None:
        self._parent = parent or self
        self._state_id = state_id
        self._value = None  # type: Any
        self._dbg_value = None
        self._depth = (parent._depth + 1) if parent is not None else 1  # type: int

    def run(self) -> None:
        pass
