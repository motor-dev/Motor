from motor_typing import TYPE_CHECKING
from .lr0item import LR0Item


class LR0Path(object):
    def __init__(self, items=tuple()):
        # type: (Tuple[Tuple[int, LR0Item],...]) -> None
        self._items = items

    def __hash__(self):
        # type: () -> int
        return hash(self._items)

    def __eq__(self, other):
        # type: (Any) -> bool
        return isinstance(other, LR0Path) and self._items == other._items

    def extend(self, item):
        # type: (LR0Item) -> LR0Path
        result = LR0Path(((0, item), ) + self._items)
        return result

    def derive_from(self, item):
        # type: (LR0Item) -> LR0Path
        result = LR0Path(((3, item), ) + self._items)
        return result

    def expand_next(self, path):
        # type: (LR0Path) -> LR0Path
        result = LR0Path(((1, path._items[0][1]), ) + path._items + ((2, path._items[0][1]), ) + self._items)
        return result

    def patch(self, original_path, new_path):
        # type: (LR0Path, LR0Path) -> LR0Path
        result = LR0Path(self._items[:-len(original_path._items)] + new_path._items)
        return result

    def _to_string(self, items, end_mark, name_map, expand_left, expand_right, add_marker):
        # type: (Tuple[Tuple[int, LR0Item], ...], Optional[Tuple[int, LR0Item]], List[str], bool, bool, bool) -> Tuple[List[Text], int, int]
        index = 0
        last_item = None
        left_sequence = tuple()    # type: Tuple[int,...]
        result = []                # type: List[Text]
        length = 0

        def merge(new_sequence, max_new_len, max_length):
            # type: (List[Text], int, int) -> int
            i = -1
            for i, (n1, n2) in enumerate(zip(new_sequence, result)):
                if n2:
                    result[i] = '%s%s%s' % (n1, ' ' * (max_new_len - len(n1) + 1), n2)
                else:
                    result[i] = n1
                max_length = max(max_length, len(result[i]))
            for add, extra in enumerate(result[i + 1:]):
                result[i + 1 + add] = ' ' * (max_new_len + 1) + extra
                max_length = max(max_length, len(result[-1]))
            for extra in new_sequence[i + 1:]:
                result.append(extra)
                max_length = max(max_length, len(extra))
            return max_length

        while index < len(items):
            op, item = items[index]
            if op == 0:
                last_item = item
                if expand_left:
                    left_sequence = item.rule.production[:item._index + 1]
                else:
                    left_sequence = item.rule.production[item._index:item._index + 1]
                index += 1
            elif op == 1:
                if last_item is None:
                    last_item = item
                elif item._index > last_item._index:
                    last_item = item
                strings, max_len, consumed_count = self._to_string(
                    items[index + 1:], (2, item), name_map, False, False, False
                )
                length = merge(strings, max_len, length)
                index += consumed_count + 1
            elif op == 2:
                if end_mark is not None:
                    assert (op, item) == end_mark
                    index += 1
                break
            elif op == 3:
                if last_item is None:
                    last_item = item
                elif item._index > last_item._index:
                    last_item = item
                strings, max_len, consumed_count = self._to_string(
                    items[index + 1:], None, name_map, expand_left, True, add_marker
                )
                derivation = name_map[item.rule.production[item._index]]
                max_len = max(max_len, len(derivation) + 2)
                extra_padding = u'\u2500' * (max_len - 2 - len(derivation))
                strings.append(u'\u2570%s%s\u256f' % (derivation, extra_padding))
                length = merge(strings, max_len, length)
                index += consumed_count + 1
                add_marker = False
            else:
                assert False
        else:
            if add_marker:
                if item._index == len(item.rule.production):
                    left_sequence = left_sequence + (1, )
                else:
                    left_sequence = left_sequence[:-1] + (1, ) + left_sequence[-1:]

        assert last_item is not None

        sequence_str = u' '.join(name_map[i] if i != 1 else '\u2666' for i in left_sequence)
        if sequence_str:
            padding = ' ' * (len(sequence_str) + 1)
            if result:
                result = [u'%s %s' % (sequence_str, result[0])] + [u'%s%s' % (padding, s) for s in result[1:]]
                length += len(sequence_str) + 1
            else:
                result = [sequence_str]
                length += len(sequence_str)
        if expand_right:
            right_sequence = last_item.rule.production[last_item._index + 1:]
            if right_sequence:
                right_sequence_str = u' '.join(name_map[i] if i != 1 else '\u2666' for i in right_sequence)
                if result:
                    result[0] += ' ' * (length - len(result[0]) + 1) + right_sequence_str
                    length += len(right_sequence_str) + 1
                else:
                    result = [right_sequence_str]
                    length += len(right_sequence_str)
        if not result:
            result = ['']
            length = 0

        return result, length, index

    def to_string(self, name_map):
        # type: (List[str]) -> List[Text]
        result, length, _ = self._to_string(self._items, None, name_map, True, True, True)
        derivation = name_map[self._items[0][1]._symbol]
        extra_padding = u'\u2500' * (length - 2 - len(derivation))
        result.append(u'\u2570%s%s\u256f' % (derivation, extra_padding))
        return result


class LR0PathItem(LR0Path):
    def __init__(self, item):
        # type: (LR0Item) -> None
        LR0Path.__init__(self, ((0, item), ))


if TYPE_CHECKING:
    from motor_typing import Any, List, Optional, Text, Tuple
    from .lr0node import LR0Node
    from .lr0item import LR0Item
