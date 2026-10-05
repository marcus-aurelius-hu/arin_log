"""
folder.py
---------
Beheert de config folder van arin_log.

Alle user-specifieke configuratie staat in één bestand:

    %APPDATA%\\arin_log\\config_log.json

Dit bestand bevat:
    - de kleuren (gekopieerd uit log_cnfg.json bij de eerste run)
    - de gekozen log_folder

Bij de eerste run wordt het bestand aangemaakt:
    1. De gebruiker kiest een log folder via de dialoog.
    2. De kleuren worden uit log_cnfg.json (package folder) gelezen.
    3. Alles wordt opgeslagen in config_log.json.

Bij volgende runs wordt alleen config_log.json gelezen.
Als het bestand corrupt is, wordt het opnieuw aangemaakt.

Publieke functies:
    get_folder()               - geeft de huidige log_folder terug
    change_folder(parent=None) - folder-dialoog, update config + log_folder
    get_config()               - geeft de volledige config dict terug

Interne functie:
    _get_folder()              - resolver, eenmalig bij import
"""

from os import path, makedirs, environ
from arin_log.utils import load_json, save_json
br = chr(10)

CNFG_FOLDER = "arin_log"
CNFG_FILE = "config_log.json"
TEMPLATE_FILE = "log_cnfg.json"


# =====================================================================
# 1. INTERNE HELPERS — paden
# =====================================================================
def _config_folder():
    """Bepaalt de config folder.

    Windows: %APPDATA%\\arin_log
    Anders:  ~/.arin_log
    Maakt de folder aan als die nog niet bestaat.
    Retourneert het pad, of False bij falen."""
    base = environ.get("APPDATA")
    if base:
        folder = path.join(base, CNFG_FOLDER)
    else:
        folder = path.join(path.expanduser("~"), ".arin_log")
    try:
        makedirs(folder, exist_ok=True)
    except Exception:
        return False
    return folder


def _config_file():
    """Pad naar config_log.json, of False."""
    folder = _config_folder()
    if not folder:
        return False
    return path.join(folder, CNFG_FILE)


def _template_file():
    """Pad naar log_cnfg.json (in de package folder)."""
    return path.join(path.dirname(__file__), TEMPLATE_FILE)


# =====================================================================
# 2. INTERNE HELPERS — config lezen en schrijven
# =====================================================================
def _read_config():
    """Leest config_log.json en retourneert de dict.
    Retourneert {} als het bestand ontbreekt."""
    pf = _config_file()
    if pf and path.isfile(pf):
        d = load_json(pf)
        if isinstance(d, dict):
            return d
    return {}


def _write_config(data):
    """Schrijft data naar config_log.json.
    Retourneert True bij succes, anders False."""
    pf = _config_file()
    if not pf:
        return False
    return save_json(pf, data, indent=4)


def _read_template():
    """Leest log_cnfg.json uit de package folder.
    Retourneert de dict, of {} als het bestand ontbreekt."""
    pf = _template_file()
    if path.isfile(pf):
        d = load_json(pf)
        if isinstance(d, dict):
            return d
    return {}


def _create_config(log_folder):
    """Maakt config_log.json aan.

    Kopieert alle sleutels uit log_cnfg.json (de template) en
    voegt 'log_folder' toe. Retourneert True bij succes."""
    d = _read_template()
    d["log_folder"] = log_folder
    return _write_config(d)


def _save_folder(folder):
    """Update alleen de 'log_folder'-key in config_log.json.
    Andere keys blijven staan. Retourneert True bij succes."""
    d = _read_config()
    if not d:
        return _create_config(folder)
    d["log_folder"] = folder
    return _write_config(d)


def _save_failed():
    """Meldt dat het opslaan is mislukt en stopt met exitcode 1."""
    from sys import stderr, exit
    stderr.write(f"folder ; selection ; not saved{br}administrator ; adjustments ; required")
    exit(1)


# =====================================================================
# 3. INTERNE HELPERS — folder keuze
# =====================================================================
def _norm(p):
    """Normaliseert een pad naar forward slashes.
    Retourneert het pad als string, of de oorspronkelijke waarde
    als die leeg is."""
    return str(p).replace("\\", "/") if p else p


def manual_input():
    """Vraagt de gebruiker om een folder via de console.

    Blijft vragen tot de gebruiker een niet-lege invoer geeft en
    de folder bestaat (of aangemaakt kan worden). Normaliseert het
    pad naar forward slashes.

    De hele lus zit in een buitenste try/except. Als er iets
    onverwachts misgaat, geeft de functie False terug in plaats
    van te crashen."""
    try:
        while True:
            gekozen = input("Enter a folder path for your log files: ")
            if not gekozen:
                continue

            gekozen = _norm(gekozen)

            if not path.isdir(gekozen):
                try:
                    makedirs(gekozen, exist_ok=True)
                except Exception:
                    print(f"Could not create folder: {gekozen}")
                    continue

            return gekozen
    except Exception:
        return False


def _folder_dialog(parent=None):
    """Opent een folder-dialoog. tkinter wordt lokaal geïmporteerd.

    parent=None -> tijdelijke verborgen root (batch-context).
    parent=<Tk> -> gebruikt de bestaande root (GUI-context).
    Retourneert het gekozen pad, of '' bij annuleren.

    Als tkinter of de GUI niet beschikbaar is, valt de functie
    terug op manual_input() (console-invoer). Als dat ook faalt,
    stopt het programma met de melding 'platform ; graphic GUI ;
    inexistent' en exitcode 1."""

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
        gekozen = manual_input()
        if gekozen:
            return gekozen
        from sys import stderr, exit
        stderr.write(f"platform ; graphic GUI ; inexistent{br}administrator ; adjustments ; required")
        exit(1)


# =====================================================================
# 4. RESOLVER — eenmalig bij import
# =====================================================================
def _get_folder():
    """Resolver: lees config_log.json, of maak het aan.

    Retourneert altijd een geldig pad (string).
    - Als config_log.json bestaat: log_folder daaruit.
    - Anders: dialoog, dan config_log.json aanmaken.
    - Bij corruptie: opnieuw aanmaken.

    Wordt eenmalig aangeroepen bij het laden van de module.
    Daarna is log_folder gezet en gebruikt de rest van de code
    die waarde via get_folder() of folder.log_folder."""
    d = _read_config()
    folder = d.get("log_folder", False)

    if folder:
        return _norm(folder)

    while True:
        gekozen = _folder_dialog()
        if gekozen:
            gekozen = _norm(gekozen)
            if not _create_config(gekozen):
                _save_failed()
            return gekozen


# =====================================================================
# 5. PUBLIEKE FUNCTIES
# =====================================================================
def get_folder():
    """Geeft de huidige log_folder terug.

    Altijd de actuele waarde. Aanroepen na change_folder() geeft
    de nieuwe folder, niet de oude. Dit is de enige juiste manier
    om de log folder op te vragen vanuit een andere module."""
    return log_folder


def change_folder(parent=None):
    """Opent de folder-dialoog, update config_log.json en de
    globale log_folder en retourneert de nieuwe waarde.

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


def get_config():
    """Geeft de volledige config dict terug uit config_log.json.

    Wordt gebruikt door logger.config_logs() om de kleuren te laden."""
    return _read_config()


# =====================================================================
# 6. TOP-LEVEL UITVOERING — log_folder is klaar na import
# =====================================================================
log_folder = _get_folder()

# =====================================================================
# 7. TESTBLOK
# =====================================================================
if __name__ == "__main__":
    print(f"log_folder: {log_folder}")
    print(f"config: {get_config()}")
    exit(0)
