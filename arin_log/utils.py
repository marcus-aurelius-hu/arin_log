from os import path
from sys import _getframe
from json import dump, load

prgnm = path.basename(__file__).split('.')[0]


def load_json(pf, logloc=None, required=True):
    """Leest een JSON-bestand en retourneert de inhoud als dict.
    Retourneert {} als het bestand ontbreekt of corrupt is.

    required=True  -> ontbrekend of corrupt bestand wordt gelogd (default).
    required=False -> ontbrekend of corrupt bestand is stil; {} wordt
                      teruggegeven zonder melding. Bedoeld voor
                      user-specifieke bestanden die de productie niet
                      mogen storen."""
    from arin_log.logger import log_except
    global prgnm
    frm = _getframe()
    logloc = prgnm if logloc is None else logloc
    jsnd = {}
    fnm = path.basename(pf)
    if path.isfile(pf):
        try:
            with open(pf, encoding='utf-8') as fil:
                jsnd = load(fil)
        except Exception:
            if required:
                log_except(frm, ' ; '.join(['data', fnm, 'corrupt']), logloc=logloc)
    else:
        if required:
            log_except(frm, ' ; '.join(['file', fnm, 'inexistent']), logloc=logloc)
    return jsnd


def save_json(pf, data, indent=None, logloc=None):
    """Schrijft data als JSON naar pf.

    indent=None of een negatief getal -> geen indentering.
    indent=<int> >= 0                 -> indentering met die breedte.

    Retourneert True bij succes, anders False.
    Bij een fout wordt de fout gelogd via log_except."""
    from arin_log.logger import log_except
    global prgnm
    frm = _getframe()
    indent = indent if isinstance(indent, int) and indent >= 0 else None
    logloc = prgnm if logloc is None else logloc
    fnm = path.basename(pf)
    try:
        with open(pf, 'w', encoding='utf-8') as fil:
            dump(data, fil, ensure_ascii=False, indent=indent)
        return True
    except Exception:
        log_except(frm, ' ; '.join(['save', fnm, 'fail']), logloc=logloc)
        return False