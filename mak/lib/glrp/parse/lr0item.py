from typing import TYPE_CHECKING


class LR0Item(object):

    def __init__(self, rule, index, next, predecessor, successors, first, follow, merge_list=[]):
        # type: (Grammar.Rule, int, Optional[LR0Item], Optional[int], List[Grammar.Rule], Set[int], Dict[int, int], List[Grammar.Merge]) -> None
        self.rule = rule
        self.len = rule.len
        self._symbol = rule._prod_symbol  # type: int
        self._index = index  # type: int
        self._previous = None  # type: Optional[LR0Item]
        self._next = next
        if next is not None:
            next._previous = self
            self._last = next._last  # type: LR0Item
        else:
            self._last = self

        self._before = predecessor
        self._after = successors
        self._symbols = frozenset(rule.production)
        self._first = first
        self._follow = follow  # type: Dict[int, int]
        self._lookaheads = {}  # type: Dict[int, List[int]]
        self._precedence = None  # type: Optional[Tuple[str, int]]
        self._split = None  # type: Optional[str]
        self._merges = tuple(merge_list)  # type: Tuple[Grammar.Merge, ...]
        self._merge_map = {}  # type: Dict[str, Grammar.Merge]
        self._merge_map_str = {}  # type: Dict[str, str]
        self._no_merge_warning = False  # type: bool

        for merge in self._merges:
            for key in merge._arguments:
                if key in self._merge_map:
                    raise SyntaxError(
                        'incorrect merge: key "%s" appears in more than one merge rule' % key,
                        (rule._filename, rule._lineno, 0, '')
                    )
                self._merge_map[key] = merge
                self._merge_map_str[key] = merge._result
        self._merge_set = frozenset(self._merge_map.keys())  # type: FrozenSet[str]
        self._split_use = 0

        if index == rule.len:
            index = -1
        annotations = rule._annotations.get(index, {})
        for annotation, values in annotations.items():
            if annotation == "prec":
                if len(values) == 1:
                    try:
                        precedence = int(values[0])
                    except ValueError:
                        raise SyntaxError(
                            'incorrect precedence: value should be an integer or a pair (string,integer), got %s' %
                            values[0], (rule._filename, rule._lineno, 0, '')
                        )
                    else:
                        self._precedence = ('nonassoc', precedence)
                elif len(values) == 2:
                    if values[0] not in ('left', 'right', 'nonassoc'):
                        raise SyntaxError(
                            'incorrect precedence: value should be an integer or a pair (string,integer), got %s' %
                            ', '.join(values), (rule._filename, rule._lineno, 0, '')
                        )
                    try:
                        precedence = int(values[1])
                    except ValueError:
                        raise SyntaxError(
                            'incorrect precedence: value should be an integer or a pair (string,integer), got %s' %
                            ', '.join(values), (rule._filename, rule._lineno, 0, '')
                        )
                    else:
                        self._precedence = (values[0], precedence)
                else:
                    raise SyntaxError(
                        'incorrect precedence: value should be an integer or a pair (string,integer), got %s' %
                        ', '.join(values), (rule._filename, rule._lineno, 0, '')
                    )
            elif annotation == "split":
                if len(values) > 1:
                    raise SyntaxError(
                        'incorrect annotation: "split" requires one argument, got %s' %
                        (','.join(values) if values else 'none'), (rule._filename, rule._lineno, 0, '')
                    )
                if len(values) == 1:
                    self._split = values[0]
                else:
                    self._split = ''
            elif annotation == "no-merge-warning":
                if len(values) != 0:
                    raise SyntaxError(
                        'incorrect annotation: "no-merge-warning" expects no argument, got %s',
                        (','.join(values) if values else 'none'), (rule._filename, rule._lineno, 0, '')
                    )
                self._no_merge_warning = True
            else:
                raise SyntaxError('unknown annotation %s' % annotation, (rule._filename, rule._lineno, 0, ''))

    def _annotations(self):
        # type: () -> str
        result = ''
        if self._precedence is not None:
            result += '[prec:%s,%d]' % self._precedence
        if self._split is not None:
            result += '[split:%s]' % self._split
        return result

    def to_string(self, name_map):
        # type: (List[str]) -> Text
        return u'%s%s -> %s \u2666 %s' % (
            name_map[self.rule._prod_symbol],
            self._annotations(),
            ' '.join([name_map[p] for p in self.rule.production[:self._index]]),
            ' '.join([name_map[p] for p in self.rule.production[self._index:]]),
        )

    def to_short_string(self, name_map):
        # type: (List[str]) -> Text
        return u'%s \u2666 %s' % (
            ' '.join([name_map[p] for p in self.rule.production[:self._index]]),
            ' '.join([name_map[p] for p in self.rule.production[self._index:]]),
        )

    def symbol(self):
        # type: () -> int
        return self.rule.production[self._index]

    def is_reduction_item(self):
        # type: () -> bool
        return self._index == self.len


if TYPE_CHECKING:
    from typing import Dict, FrozenSet, List, Optional, Set, Text, Tuple
    from .grammar import Grammar, MergeAction
