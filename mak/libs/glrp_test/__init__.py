from . import parser
import sys


def run():
    # type: () -> None
    try:
        #parser.Parser1()
        #parser.Parser2()
        #parser.Parser3()
        #parser.Parser4()
        #parser.Parser5()
        #parser.Parser6()
        parser.Parser7()
    except SyntaxError as exception:
        print(exception)
        sys.exit(255)
