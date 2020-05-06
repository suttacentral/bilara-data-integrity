import logging
import re

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)

is_it_a_sutta = re.compile(r"""
[a-zA-Z]+           # Sutta IDs start with letters.
(-[a-zA-Z]*)*       # They may contain hyphens.
[1-9]\d*            # And must have a number
([.][1-9]\d*)?      # Or two numbers, e.g. sn1.1.
(-[1-9]\d*)?        # Baked suttas, e.g. sn56.105-107.
$
""", re.VERBOSE)

is_it_a_segment = re.compile(r"""
[a-zA-Z]+           # (Same as above)
(-[a-zA-Z]*)*       #
[1-9]\d*            #
([.][1-9]\d*)?      #
(-[1-9]\d*)?        #
:                   #
(\d|[1-9]\d+)       # Each segment ID begins with a number...
[.]                 # ...followed by a dot...
(\d|[1-9]\d+)       # ...and once more a number.
([.](\d|[1-9]\d+))* # Segments may contain more numbers and dots.
$
""", re.VERBOSE)

def checking_uid(cfg: Config):
    sutta_mn = cfg.repo.get_example()
    log.info("sutta_mn: %s", sutta_mn)
