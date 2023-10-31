from typing import List


class mach_header(object):
    def __init__(self) -> None:
        self.cputype: int = ...
        self.cpusubtype: int = ...


class MachOHeader(object):
    def __init__(self) -> None:
        self.header: mach_header = ...


class MachO(object):
    def __init__(self, filename: str) -> None:
        self.headers: List[MachOHeader] = ...
