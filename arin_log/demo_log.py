"""
demo_log.py
-----------
Eerste kennismaking met arin_log.

Laat zien:
    - hoe je een hoofdmodule markeert met log_start / log_exit
    - hoe je een exception logt met log_except
    - hoe je console-output en logbestand-uitvoer combineert
      via de logloc-parameter

Draai met:
    python -m arin_log.demo_log
"""

from arin_log.logger import log_start, log_notes, log_except, log_exit
from sys import _getframe
from os import path

prgnm = path.basename(__file__).split('.')[0]

def demo():
    log_start(prgnm, logloc=prgnm)

    log_notes("demo ; test ; logger")

    try:
        1 / 0
    except Exception:
        log_except(_getframe(), "zero ; division ; exception", logloc=prgnm)

    log_notes("continuing ; logging ; success")
    log_notes("demo ; test ; success", logloc=prgnm)
    log_exit(prgnm, logloc=prgnm)

if __name__ == "__main__":
    demo()
