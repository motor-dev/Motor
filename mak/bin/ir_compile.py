import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), 'vendor'))

import ircc

if __name__ == '__main__':
    ircc.run()
