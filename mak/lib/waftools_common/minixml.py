from typing import Dict, IO, Iterable, List, Optional, Tuple, Type, Union
from types import TracebackType


def _xmlify(s: str) -> str:
    s = s.replace("&", "&amp;")  # do this first
    s = s.replace("'", "&apos;")
    s = s.replace('"', "&quot;")
    return s


class XmlDocument(object):
    def __init__(
            self,
            file: IO[str],
            encoding: str,
            processing_instructions: Optional[List[Tuple[str, str]]] = None
    ) -> None:
        self.file = file
        self.file.write('<?xml version="1.0" encoding="%s" standalone="no"?>\n' % encoding)
        if processing_instructions is not None:
            for instruction in processing_instructions:
                self.file.write('<!%s %s>\n' % instruction)
        self.closed = False
        self.empty = False
        self.current = None  # type: Optional["XmlNode"]
        self.indent = -1

    def __enter__(self) -> "XmlDocument":
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> Optional[bool]:
        self.close()
        return None

    def close(self) -> None:
        self.file.close()

    def add(self, node: "XmlNode") -> None:
        assert not self.closed
        assert self.current is None
        if self.empty:
            self.begin()
        self.empty = False
        self.current = node

    def begin(self) -> None:
        raise NotImplementedError


class XmlNode(object):
    def __init__(
            self,
            parent: Union[XmlDocument, "XmlNode"],
            name: str,
            text: str = '',
            attributes: Union[None, Iterable[Tuple[str, str]]] = None) -> None:
        self.parent = parent
        self.current = None  # type: Optional["XmlNode"]
        self.name = name
        self.indent = parent.indent + 1  # type: int
        self.file = parent.file  # type: IO[str]
        self.closed = False
        self.empty = True
        parent.add(self)
        self.open(text, attributes)

    def __enter__(self) -> "XmlNode":
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> Optional[bool]:
        if not self.closed:
            self.close()
        return None

    def add(self, node: "XmlNode") -> None:
        assert not self.closed
        assert self.current is None
        if self.empty:
            self.begin()
        self.empty = False
        self.current = node

    def open(self, text: str = '', attributes: Union[None, Iterable[Tuple[str, str]]] = None) -> None:
        self.file.write('%s<%s' % (' ' * self.indent, self.name))
        if attributes:
            if isinstance(attributes, dict):
                for key, value in attributes.items():
                    self.file.write(' %s="%s"' % (key, value))
            else:
                for key, value in attributes:
                    self.file.write(' %s="%s"' % (key, value))
        if text:
            self.file.write('>%s</%s>\n' % (_xmlify(text), self.name))
            assert (self.parent.current == self)
            self.parent.current = None
            self.closed = True
            self.empty = False

    def close(self) -> None:
        if not self.closed:
            assert (self.parent.current == self)
            self.parent.current = None
            if self.empty:
                self.file.write(' />\n')
            else:
                self.file.write('%s</%s>\n' % (' ' * self.indent, self.name))

    def begin(self) -> None:
        self.file.write('>\n')
        self.empty = False
