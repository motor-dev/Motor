from .cl_generator import ClDeclaration, ClDefinition
from motor_typing import TYPE_CHECKING


def generators(file):
    # type: (TextIO) -> Generator[IrccGenerator, None, None]
    yield ClDeclaration(file)
    yield ClDefinition(file)


if TYPE_CHECKING:
    from typing import Generator, TextIO
    from ircc import IrccGenerator