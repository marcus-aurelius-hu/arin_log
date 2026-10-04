"""
folder.py
---------
Minimalistische, stabiele module voor het afhandelen van de
environment variabele 'arin_log' en de bijhorende log folder
('log_folder').

Gebruik in andere modules (enige import die nodig is):

    from folder import log_folder

Bij de eerste import wordt de volledige logica uitgevoerd:
    1. Lees env['arin_log'].
    2. Als 'folder' aanwezig is -> log_folder = die folder.
    3. Anders -> folder-dialoog (tkinter wordt lokaal geïmporteerd).
         - User kiest -> env wordt geüpdatet (alleen 'folder'-key),
           log_folder = gekozen folder.
         - User annuleert -> de dialoog verschijnt opnieuw.
           De gebruiker moet een keuze maken; er is geen fallback.

Vanaf de tweede keer dat een module importeert, is 'folder' aanwezig
in de env en wordt er geen tkinter meer geladen — geen dialoog, geen
overhead.

Publieke functies:
    getEnv(key)               - lees env-variabele (user-level)
    setEnv(key, val)          - schrijf env-variabele (user-level)
    get_folder()              - herbereken log_folder
                                (zelfde logica als bij import)
    change_folder(parent=None) - folder-dialoog, update env + log_folder,
                                 retourneert de nieuwe waarde
                                 (of False bij annuleren)
"""

from json import loads, dumps
from py_setenv import setenv
br = chr(10)

# =====================================================================
# 1. ENV-TOEGANG
# =====================================================================
def getEnv(key):
    """Leest een env-variabele op user-niveau.
    Retourneert de waarde als string, of False bij leeg/afwezig."""
    val = setenv(key, user=True, suppress_echo=True)
    if val == '':
        val = False
    return val


def setEnv(key, val):
    """Schrijft een env-variabele op user-niveau.
    Retourneert True bij succes, anders False."""
    try:
        setenv(key, value=val, user=True, suppress_echo=True)
        return True
    except Exception:
        return False


# =====================================================================
# 2. INTERNE HELPERS
# =====================================================================
def _read_folder():
    """Leest env['arin_log'] en retourneert een dict.

    - Geldige JSON-dict          -> die dict
    - Geldige JSON, geen dict    -> {} (geen folder)
    - Geen geldige JSON (plat)   -> {"folder": <raw>}  (backward compat)
    - Geen waarde                -> {}
    """
    raw = getEnv("arin_log")
    if not raw:
        return {}

    try:
        d = loads(raw)
    except Exception:
        # Geen geldige JSON -> platte folder-string (backward compat)
        return {"folder": raw}

    if isinstance(d, dict):
        return d
    return {}


def _save_folder(folder):
    """Update ALLEEN de 'folder'-key in env['arin_log'].
    Andere keys (plot, save, ...) blijven ongemoeid.
    Retourneert True bij succes, anders False."""
    d = _read_folder()
    d["folder"] = folder
    try:
        return setEnv("arin_log", dumps(d))
    except Exception:
        return False


def _save_failed():
    """Meldt dat het opslaan van de folderkeuze is mislukt en stopt
    het programma met exitcode 1. Er is geen fallback; de gebruiker
    of de administrator moet ingrijpen."""
    from sys import stderr, exit
    stderr.write(f"folder ; selection ; not saved{br}administrator ; adjustments ; required")
    exit(1)


def _folder_dialog(parent=None):
    """Opent een folder-dialoog. tkinter wordt lokaal geïmporteerd.

    parent=None -> tijdelijke verborgen root (batch-context).
    parent=<Tk> -> gebruikt de bestaande root (GUI-context).
    Retourneert het gekozen pad, of '' bij annuleren.

    Als tkinter of de GUI niet beschikbaar is, stopt het programma
    met de melding 'platform ; graphic GUI ; inexistent' en exitcode 1.
    Er is geen fallback; de gebruiker moet een grafische omgeving hebben."""

    try:
        from tkinter import Tk, filedialog

        root = None
        folder = ""
        eigen_root = False
        if parent is None:
            root = Tk()
            root.withdraw()
            eigen_root = True
            parent = root
        try:
            folder = filedialog.askdirectory(
                parent=parent,
                title="Choose a folder for your log files"
            )
        finally:
            if eigen_root:
                try:
                    root.destroy()
                except Exception:
                    pass

        return folder if folder else ""

    except Exception:
        from sys import stderr, exit
        stderr.write(f"platform ; graphic GUI ; inexistent{br}administrator ; adjustments ; required")
        exit(1)


def _norm(p):
    """Normaliseert een pad naar forward slashes.
    Retourneert het pad als string, of de oorspronkelijke waarde
    als die leeg is."""
    return str(p).replace("\\", "/") if p else p


def get_folder():
    """Hoofdlogica: env -> dialoog (blijven vragen tot keuze).

    Retourneert altijd een geldig pad (string).
    Bij een geldige 'folder'-key in env: dat pad.
    Anders: de dialoog blijft verschijnen tot de gebruiker een map
    kiest. Er is geen fallback; de gebruiker moet kiezen.
    De gebruiker kan het script altijd afsluiten met Ctrl+C.

    Als de keuze niet opgeslagen kan worden, stopt het programma
    met de melding 'folder ; selection ; not saved' en exitcode 1."""
    d = _read_folder()
    folder = d.get("folder", False)

    if folder:
        return _norm(folder)

    while True:
        gekozen = _folder_dialog()
        if gekozen:
            gekozen = _norm(gekozen)
            if not _save_folder(gekozen):
                _save_failed()
            return gekozen


# =====================================================================
# 3. PUBLIEKE FUNCTIE — folder wijzigen
# =====================================================================
def change_folder(parent=None):
    """Opent de folder-dialoog, slaat de gekozen folder op in env,
    updatet de globale log_folder en retourneert de nieuwe waarde.

    parent=None -> tijdelijke verborgen root (batch-context).
    parent=<Tk> -> gebruikt de bestaande root (GUI-context).

    Bij annulering: retourneert False, log_folder blijft ongewijzigd.
    Retourneert het nieuwe pad (string) bij succes.

    Als de keuze niet opgeslagen kan worden, stopt het programma
    met de melding 'folder ; selection ; not saved' en exitcode 1."""
    global log_folder

    gekozen = _folder_dialog(parent=parent)
    if not gekozen:
        return False

    gekozen = _norm(gekozen)
    if not _save_folder(gekozen):
        _save_failed()
    log_folder = gekozen
    return log_folder


# =====================================================================
# 4. TOP-LEVEL UITVOERING — log_folder is klaar na import
# =====================================================================
log_folder = get_folder()

# =====================================================================
# 5. TESTBLOK
# =====================================================================
if __name__ == "__main__":
    print(f"log_folder: {log_folder}")
    exit(0)
