from os import path
from json import dump, load

# Vaste ANSI-kleuren voor _warn.
# Los van de user-config (log_cnfg.json), omdat utils.py een blad is
# en geen toegang heeft tot de logger.
# Kleurcodes uit log_cnfg.json: cyan=36m, pink=95m, lightred=91m.
_CYAN = "\033[36m"
_RESET = "\033[00m"


def _warn(note, word, color):
    """Print een waarschuwing op de console.

    'Arin' wordt altijd cyaan. Het opgegeven woord krijgt de
    opgegeven kleurcode. Wordt alleen gebruikt bij interne fouten
    in utils.py (corrupt of ontbrekend bestand).

    Deze functie staat los van de logger: utils.py is een blad en
    mag niet van logger afhangen (zou een circulaire import geven)."""
    note = note.replace(word, f"\033[{color}{word}{_RESET}")
    print(f"{_CYAN}Arin{_RESET} : {note}")
    return


def load_json(pf):
    """Leest een JSON-bestand en retourneert de inhoud als dict.
    Retourneert {} als het bestand ontbreekt of corrupt is.

    Bij ontbreken of corruptie wordt een melding op de console
    geprint, met Arin-prefix en vaste kleuren."""
    jsnd = {}
    fnm = path.basename(pf)
    if path.isfile(pf):
        try:
            with open(pf, encoding='utf-8') as fil:
                jsnd = load(fil)
        except Exception:
            _warn(f"data ; {fnm} ; corrupt", "corrupt", "95m")
    else:
        _warn(f"file ; {fnm} ; inexistent", "inexistent", "91m")
    return jsnd


def save_json(pf, data, indent=None):
    """Schrijft data als JSON naar pf.

    indent=None of een negatief getal -> geen indentering.
    indent=<int> >= 0                 -> indentering met die breedte.

    Retourneert True bij succes, anders False.
    Bij een fout wordt een melding op de console geprint."""
    indent = indent if isinstance(indent, int) and indent >= 0 else None
    fnm = path.basename(pf)
    try:
        with open(pf, 'w', encoding='utf-8') as fil:
            dump(data, fil, ensure_ascii=False, indent=indent)
        return True
    except Exception:
        _warn(f"save ; {fnm} ; fail", "fail", "91m")
        return False