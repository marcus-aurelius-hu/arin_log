"""
console.py
----------
Console-interactie voor arin_log.

Bevat:
    cls()                    - wist het scherm (Windows: cls, anders clear)
    menu_dict(optlst)        - bouwt een dict van genummerde menu-opties
    cons_menu(optlst, ...)   - toont een console-menu en retourneert
                               de gekozen functie als commando-string.

Dit is een aparte module omdat console-interactie (menu, scherm wissen)
niets met loggen te maken heeft. De logger logt; de console toont.
"""

from os import system, name, path
from arin_log.logger import log_notes

br = chr(10)
prgnm = path.basename(__file__).split('.')[0]


def cls():
    """Wist het scherm. Op Windows met 'cls', anders met 'clear'."""
    system('cls' if name == 'nt' else 'clear')
    return


def menu_dict(optlst):
    """Bouwt een dict van genummerde menu-opties.

    De opties krijgen de sleutels '1', '2', '3', ... in volgorde.
    Daarnaast worden de aliassen 'e', 'exit', 'q' en 'quit' toegevoegd,
    die allemaal naar 'exit' wijzen."""
    opties = {}
    idx = 1
    for opt in optlst:
        ids = str(idx)
        opties[ids] = opt
        idx += 1
    opties['e'] = 'exit'
    opties['exit'] = 'exit'
    opties['q'] = 'exit'
    opties['quit'] = 'exit'
    return opties


def cons_menu(optlst, logloc=None):
    """Toont een console-menu en retourneert de gekozen functie
    als een commando-string (bijvoorbeeld 'mijn_functie()').

    optlst   - lijst met functienamen (strings, zonder haakjes).
               'exit' wordt automatisch toegevoegd als het ontbreekt.
    logloc   - context voor de logger; standaard None.

    De functie blijft het menu tonen tot de gebruiker een geldige
    keuze maakt. 'exit', 'e', 'q' en 'quit' geven 'exit(0)' terug."""

    exts = ['e', 'exit', 'q', 'quit']
    tlst = optlst
    if 'exit' not in tlst:
        tlst.append('exit')

    opties = menu_dict(tlst)
    keys = list(opties.keys())
    lng = len(keys)
    choice = '#'
    com = ''
    while choice not in keys:
        cls()
        log_notes([f'{logloc} ; console ; menu', br])
        for key in keys:
            tmp = opties[key].replace('_', ' ')
            if key not in exts:
                print(f'{key}. {tmp}')
        print()
        choice = input(f'Enter your choice ({keys[0]}-{keys[-5]}): ')
        if choice.lower() in exts:
            choice = choice.lower()
        cls()
        if choice in keys:
            com = opties[choice]
            tmp = opties[choice].replace('_', ' ')
            x = keys.index(choice)
            if x < lng - 5:
                log_notes([br, f'Your ; choice ; {tmp}'], logloc=logloc)
            if com.lower() == 'exit':
                com = 'exit(0)'
            else:
                com = f'{com}()'
    return com