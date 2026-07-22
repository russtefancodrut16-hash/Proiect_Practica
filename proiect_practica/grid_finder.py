''' Gaseste tabla de Minesweeper clasic pe ecran: cauta patratele gri de
fundal, le aranjeaza intr-o grila, deduce dimensiunea tablei.

Calibrat pentru scala de ecran 100% (Windows Display Settings). La alta
scala, nu va gasi tabla corect.
'''

from dataclasses import dataclass

import numpy as np
from PIL import ImageDraw


# Culoarea de fundal a unei casute acoperite, in skin-ul clasic (XP/98)
CULOARE_FUNDAL = [(192, 192, 192), (192, 192, 192, 255)]

# Dimensiuni de tabla "normale" pentru minesweeper clasic, cu numarul
# standard de mine pentru fiecare
DIMENSIUNI_CUNOSCUTE = {
    (8, 8): 10,
    (9, 9): 10,
    (16, 16): 40,
    (30, 16): 99,
}

DIMENSIUNE_MINIMA_CASUTA = 10


@dataclass
class TablaGasita:
    ''' Rezultatul gasirii tablei pe ecran. '''
    coordonate: np.ndarray  # array (coloane, randuri, 4) cu (left,top,right,bottom)
    latime: int             # numar de coloane
    inaltime: int           # numar de randuri
    mine: int                # numarul de mine (dedus sau necunoscut=0)


def gaseste_tabla(screenshot, mine_impuse=None):
    ''' Cauta tabla de minesweeper in screenshot (imagine PIL).
    Returneaza un TablaGasita, sau None + un mesaj de eroare daca nu a
    gasit-o / a gasit ceva inconsistent.

    IN: screenshot - imagine PIL (ex: pyautogui.screenshot())
        mine_impuse - daca stii sigur numarul de mine, il poti forta aici
    OUT: (TablaGasita sau None, mesaj_pentru_om)
    '''
    pixels = screenshot.load()
    latime_img, inaltime_img = screenshot.size

    def gaseste_patrat(left, top):
        culoare = pixels[left, top]
        right = left
        while right < latime_img - 1 and pixels[right + 1, top] == culoare:
            right += 1
        bottom = top
        while bottom < inaltime_img - 1 and pixels[left, bottom + 1] == culoare:
            bottom += 1
        for i in range(left, right + 1):
            for j in range(top, bottom + 1):
                if pixels[i, j] != culoare:
                    return None
        return left, top, right, bottom

    # Cautam toate patratele posibile, pictandu-le peste dupa ce le gasim
    # ca sa nu le numaram de doua ori
    desen = ImageDraw.Draw(screenshot)
    gasite = []
    for i in range(latime_img):
        for j in range(inaltime_img):
            if pixels[i, j] not in CULOARE_FUNDAL:
                continue
            rezultat = gaseste_patrat(i, j)
            if rezultat is None:
                continue
            left, top, right, bottom = rezultat
            lat, inal = right - left, bottom - top
            if lat > DIMENSIUNE_MINIMA_CASUTA and inal > 0 and 0.9 < lat / inal < 1.1:
                gasite.append((left, top, right, bottom))
                desen.rectangle((left, top, right, bottom), fill="black")
            else:
                desen.line((left, top, right, top), fill="black")
                desen.line((left, top, left, bottom), fill="black")

    if len(gasite) < 10:
        return None, "Nu am gasit nicio tabla pe ecran (prea putine patrate gri gasite)."

    # Pastram doar patratele care sunt pe o grila reala (coordonate care
    # se repeta des - o casuta izolata, gasita din greseala, nu se repeta)
    x_count, y_count = {}, {}
    for left, top, right, bottom in gasite:
        for cheie, dic in ((left, x_count), (right, x_count), (top, y_count), (bottom, y_count)):
            dic[cheie] = dic.get(cheie, 0) + 1

    ponderi = []
    for left, top, right, bottom in gasite:
        pondere = x_count[left] + x_count[right] + y_count[top] + y_count[bottom]
        ponderi.append(pondere)
    prag = sorted(ponderi)[len(ponderi) // 2]
    gasite_filtrate = [g for g, p in zip(gasite, ponderi) if p >= prag]

    latime = len(set(g[0] for g in gasite_filtrate))
    inaltime = len(set(g[1] for g in gasite_filtrate))

    asteptate = latime * inaltime
    if len(gasite_filtrate) != asteptate:
        return None, (
            f"Am gasit {len(gasite_filtrate)} patrate, dar dimensiunea "
            f"dedusa ({latime}x{inaltime}) ar insemna {asteptate}. Nu se "
            "potrivesc - tabla nu a fost identificata corect. Verifica "
            "ca jocul e complet vizibil, la scala de ecran 100%, si ca "
            "nu il acopera nimic."
        )

    # Sortam patratele in ordinea (coloana, rand)
    gasite_filtrate.sort(key=lambda g: (g[0], g[1]))
    coordonate = np.array(gasite_filtrate, dtype=object).reshape(latime, inaltime, 4)

    mine = mine_impuse
    if mine is None:
        mine = DIMENSIUNI_CUNOSCUTE.get((latime, inaltime), 0)

    tabla = TablaGasita(coordonate=coordonate, latime=latime, inaltime=inaltime, mine=mine)

    mesaj = f"Tabla gasita: {latime} x {inaltime}, {mine} mine."
    if (latime, inaltime) not in DIMENSIUNI_CUNOSCUTE:
        mesaj += (
            f" Atentie: {latime}x{inaltime} nu e o dimensiune standard "
            f"({sorted(DIMENSIUNI_CUNOSCUTE)}) - poate fi o tabla "
            "personalizata (OK), sau semn ca ceva nu e in regula."
        )
    return tabla, mesaj
