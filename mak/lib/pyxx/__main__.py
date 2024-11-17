import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SCRIPT_DIR)

from pyxx import init_arguments, run

if __name__ == '__main__':
    arguments = init_arguments()
    run(arguments.parse_args())
