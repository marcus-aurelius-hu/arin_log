"""
logger.py
---------
Centrale logging-module van arin_log.

Ondersteunende modules:
    folder.py   - beheert de config en de log folder.
    utils.py    - algemene helpers (load_json, save_json).
    console.py  - console-interactie (menu, scherm wissen).

Publieke functies:
    log_start, log_notes, log_except, log_exit, config_logs,
    file_exist, tijd, not_set, last_record.
"""

from os import path, makedirs
from sys import _getframe, stderr, exit
from gc import collect
from re import sub
import time

from arin_log import folder

color_words = {}
color_codes = {}
prgnm = ''
tas = ''
tas2 = ''
br = chr(10)
recs_dic = {}


def not_set():
    global prgnm
    isns = True if prgnm == '' else False
    return isns


def tijd():
    return time.strftime("%H:%M:%S")


def last_record(logloc):
    global recs_dic, br
    result = recs_dic.get(logloc, br)
    return result


def to_cons(note):
    """Print note naar de console, met kleuren volgens color_words
    en color_codes. Woorden worden alleen gekleurd als ze exact
    overeenkomen (inclusief spaties)."""
    global color_words, color_codes
    clrlst = list(color_words.keys())
    if any([x in note for x in clrlst]):
        for w in clrlst:
            if w in note:
                tmp = sub(r'[^\w\s]', '', note)
                tmp = sub(' +', ' ', tmp)
                nwlst = tmp.split(' ')
                twl = w.split(' ')
                if all([x in nwlst for x in twl]):
                    clr = color_words.get(w, None)
                    clrc = color_codes.get(clr, None)
                    if clrc is not None:
                        note = note.replace(w, f"\033[{clrc}{w}\033[00m")
    print(note)
    return


def to_file(data, logloc=None):
    global br, recs_dic
    frm = _getframe()
    logloc = 'error' if logloc is None else logloc
    fnm = '.'.join([tas2, logloc, 'log'])
    pf = path.join(folder.log_folder, fnm)
    act = 'a' if path.isfile(pf) else 'w'
    if isinstance(data, list):
        records = data
    else:
        records = [str(data)]
    ln = len(records)
    if ln > 0:
        try:
            with open(pf, act, encoding="utf-8") as txtFile:
                for rec in records:

                    if (last_record(logloc) == br) and (rec == br):
                        continue
                    else:
                        if rec == br:
                            recs_dic[logloc] = br
                            rec = ''
                        else:
                            recs_dic[logloc] = 'ne'
                        rec = rec + br
                        txtFile.write(rec)

                        if any([x in rec for x in ['completed', 'terminated']]):
                            lng = len(rec)
                            if 'completed' in rec:
                                lijn = '-' * (lng - 1) + br
                            elif 'terminated' in rec:
                                lijn = '_' * (lng - 1) + br
                            txtFile.write(lijn)
                            recs_dic[logloc] = 'ne'
                txtFile.close()
        except Exception:
            st = ' ; '.join(['logging', fnm, 'fail'])
            log_except(frm, st, mod=prgnm, logloc=logloc)
    else:
        st = ' ; '.join(['log', fnm, 'empty'])
        log_except(frm, st, mod=prgnm, logloc=logloc)
    return


def log_notes(notes, cons=None, logloc=None, end=False, ar_on=True):
    """Schrijft notes naar de console (indien cons=True) en naar het
    logbestand (indien logloc is meegegeven).

    end=True  -> gebruik 'Arin' als prefix (voor afsluitende berichten).
    end=False -> gebruik 'Arin :' als prefix (of geen prefix als ar_on=False).
    """
    global br, prgnm
    cons = True if cons is None else cons
    st = False if logloc is None else True
    if isinstance(notes, str):
        notes = [notes]
    for el in notes:
        if cons:
            if end:
                if el == br:
                    print()
                else:
                    to_cons(' '.join(['Arin', el]))
            else:
                if el == br:
                    print()
                elif ar_on:
                    to_cons(' '.join(['Arin :', el]))
                else:
                    to_cons(el)
        if st:
            to_file(el, logloc=logloc)
    return


def log_start(pnm, imp=None, cons=None, logloc=None):
    """Markeert het begin van een module-run en ververst de datum
    waarop het logbestand is gebaseerd (tas2). Zo komt een run die
    na middernacht start in het logbestand van de nieuwe dag."""
    global br, tas2
    imp = False if imp is None else imp
    typ = 'pending' if imp else 'running'
    cons = True if cons is None else cons
    tas2 = time.strftime('%y-%m-%d')
    lijn = ' ; '.join([pnm, tijd(), typ])
    if last_record(logloc) != br:
        lijn = [br, lijn]
    if not imp:
        lijn = [lijn, br]
    log_notes(lijn, cons=cons, logloc=logloc)
    return


def log_except(frm, note, mod=None, cons=None, logloc=None):
    global br
    logloc = 'error' if logloc is None else logloc
    cons = True if cons is None else cons
    if last_record(logloc) == br:
        notes = []
    else:
        notes = [br]
    flpf = frm.f_code.co_filename
    mod = path.basename(flpf).split('.')[0] if mod is None else mod
    fncpos = '.'.join([mod, frm.f_code.co_name, str(frm.f_lineno)])
    lijn = ' ; '.join([fncpos, tijd(), 'exception'])
    notes.append(lijn)
    if isinstance(note, str):
        notes.append(note)
    elif isinstance(note, list):
        notes = notes + note
    log_notes(notes, logloc=logloc, cons=cons)
    return


def log_exit(prginf, imp=None, cons=None, logloc=None):
    global br
    imp = False if imp is None else imp
    cons = True if cons is None else cons
    notes = [prginf] if isinstance(prginf, str) else prginf
    if imp:
        notes[-1] = ' ; '.join([notes[-1], tijd(), 'completed'])
    else:
        if last_record(logloc) != br:
            notes = [br] + notes
        notes[-1] = ' ; '.join([notes[-1], tijd(), 'terminated'])
    notes.append(br)
    log_notes(notes, logloc=logloc, cons=cons)
    collect()
    if imp:
        return
    else:
        import sys
        sys.tracebacklimit = 0
        sys.exit(0)


def config_logs():
    """Leest de kleuren uit config_log.json (via folder.get_config)
    en zet ze als globals.

    De sleutel 'log_folder' wordt overgeslagen; die hoort bij folder.py."""
    jsnd = folder.get_config()
    if len(jsnd) > 0:
        for k in jsnd.keys():
            if k == "log_folder":
                continue
            globals()[k] = jsnd.get(k, False)
    return


def file_exist(pf, timeout=None):
    from time import sleep
    timeout = 0.24 if timeout is None else timeout
    if pf is None:
        return False
    else:
        st = True
        slt = 0.08
        tt = 0
        while not path.isfile(pf):
            tt = tt + slt
            if tt >= timeout:
                st = False
                break
            sleep(slt)
    return st


def _ensure_log_folder():
    """Controleert of folder.log_folder bestaat en maakt hem zo nodig
    aan. Lukt dat niet, dan stopt het programma met een duidelijke
    melding op stderr en exitcode 1."""
    try:
        makedirs(folder.log_folder, exist_ok=True)
    except Exception:
        stderr.write(f"log ; folder ; inexistent{br}administrator ; adjustments ; required")
        exit(1)
    return


if not_set():
    prgnm = path.basename(__file__).split('.')[0]
    tas2 = time.strftime('%y-%m-%d')
    tas = time.strftime('%Y-%m-%d')
    _ensure_log_folder()
    config_logs()


if __name__ == "__main__":
    from arin_log.demo_log import demo
    demo()
    exit(0)

