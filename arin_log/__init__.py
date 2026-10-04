"""
arin_log
--------
Een lichtgewicht, platformonafhankelijke logging-package voor
langlopende pipelines.

Twee rollen in één package:

1. Een virtuele assistent (Arin) die op de console tegen de gebruiker
   praat en hem op de hoogte houdt van wat het script doet.
2. Een schoon, technisch logbestand dat alleen de bakens bevat:
   start, exception, exit. Bedoeld voor de ontwikkelaar die later
   moet reconstrueren wat er is gebeurd.

De gebruiker ziet een verhaal. De ontwikkelaar ziet een spoor.

Publieke API
------------
Vanuit de logger:
    log_start, log_notes, log_except, log_exit,
    config_logs, file_exist, tijd

Vanuit de folder:
    log_folder, change_folder

Vanuit de console:
    cons_menu

Interne functies blijven bereikbaar via hun eigen module, bijvoorbeeld:
    from arin_log.logger import not_set
    from arin_log.folder import getEnv, setEnv, get_folder
    from arin_log.utils import load_json, save_json
    from arin_log.console import cls, menu_dict
"""

__version__ = "0.1.0"

from arin_log.logger import (
    log_start,
    log_notes,
    log_except,
    log_exit,
    config_logs,
    file_exist,
    tijd,
)

from arin_log.folder import (
    log_folder,
    change_folder,
)

from arin_log.console import (
    cons_menu,
)

__all__ = [
    "log_start",
    "log_notes",
    "log_except",
    "log_exit",
    "config_logs",
    "file_exist",
    "tijd",
    "log_folder",
    "change_folder",
    "cons_menu",
]