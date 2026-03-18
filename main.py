"""DDOLoot entry point — run with: python main.py [options]

See ddo_sync.cli for full documentation and option reference.
"""

import sys
from ddo_sync.cli import main

if __name__ == "__main__":
    sys.exit(main())
