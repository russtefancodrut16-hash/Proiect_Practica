''' Cititor de ecran pentru Minesweeper clasic (skin XP/98/Minesweeper X),
FARA poze capturate manual.

Ideea: Minesweeper clasic foloseste culori FIXE, standard, pentru fiecare
cifra (1=albastru, 2=verde, 3=rosu, 4=bleumarin, 5=grena, 6=turcoaz,
7=negru, 8=gri) si un fundal gri fix (192,192,192). In loc sa comparam
fiecare casuta cu poze capturate manual (fragil - depinde de mouse
pozitionat perfect, praguri de sensibilitate etc), recunoastem direct:

  - acoperit vs deschis: dupa reliefu 3D (colt stanga-sus luminos,
    colt dreapta-jos umbrit = buton "ridicat" = acoperit)
  - cifre 1-8: dupa culoarea dominanta din casuta
  - mina: un "bulgare" de pixeli negri, plin (nu o cifra subtire)
  - steag: un mic desen rosu+negru, dar fundalul ramane gri (nu tot rosu)
  - mina explodata: fundal MAJORITAR rosu

Avantaje fata de metoda cu poze:
  - Zero setup manual, zero capture_samples.py
  - Nu exista ambiguitate "0 vs acoperit" (le desparte testul de relief,
    nu o comparatie de imagine unde pot iesi aproape identice)
  - Testabil offline cu imagini generate sintetic (vezi test_screen_reader.py)
'''

import minesweeper_game as mg


# Fundalul standard al unei casute in skin-ul clasic
FUNDAL_GRI = (192, 192, 192)

# Culorile standard ale cifrelor in Minesweeper clasic.
# 7 lipseste intentionat de-aici - e negru, la fel ca mina, si il
# despartim de mina dupa FORMA (vezi _distinge_negru_cifra7_sau_mina),
# nu dupa culoare.
CULORI_CIFRE = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    # 8 NU e aici intentionat - e gri (128,128,128), prea aproape de
    # umbre/margini/zgomot ca sa fie prinsa sigur printr-o simpla
    # potrivire de culoare (facea pixeli zgomotosi de langa orice forma
    # sa fie confundati cu "8"). E detectata separat, mai atent, de
    # _numara_gri_mediu_interior de mai jos.
}


def _e_gri(pixel, toleranta=18):
    ''' Un pixel e "gri" (fara culoare) daca cele 3 canale sunt apropiate
    intre ele - acopera fundalul, muchiile, umbrele si highlight-urile.
    NU acopera negru pur / aproape pur in mod special - il tratam separat
    ca "intunecat", ca sa putem recunoaste cifra 7 si mina.
    '''
    r, g, b = pixel[:3]
    return (max(r, g, b) - min(r, g, b)) <= toleranta


def _e_intunecat(pixel, prag=70):
    r, g, b = pixel[:3]
    return r < prag and g < prag and b < prag


def _e_rosu(pixel):
    r, g, b = pixel[:3]
    return r > 140 and g < 100 and b < 100


def _distanta_culoare(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def _cea_mai_apropiata_cifra(pixel, prag_distanta=110 ** 2):
    ''' Gaseste cea mai apropiata culoare de cifra cunoscuta.
    Returneaza None daca nu e destul de aproape de nicio culoare stiuta
    (mai bine sa raportam "nu stiu" decat sa ghicim gresit).
    '''
    cea_mai_buna, cea_mai_buna_dist = None, None
    for cifra, culoare in CULORI_CIFRE.items():
        dist = _distanta_culoare(pixel[:3], culoare)
        if cea_mai_buna_dist is None or dist < cea_mai_buna_dist:
            cea_mai_buna_dist = dist
            cea_mai_buna = cifra
    if cea_mai_buna_dist is not None and cea_mai_buna_dist <= prag_distanta:
        return cea_mai_buna
    return None


def _medie_patch(pixels, cx, cy, raza, latime, inaltime):
    ''' Media culorii intr-un mic patrat in jurul (cx,cy), ca sa nu ne
    bazam pe un singur pixel (zgomotos).
    '''
    total = [0, 0, 0]
    n = 0
    for x in range(max(0, cx - raza), min(latime, cx + raza + 1)):
        for y in range(max(0, cy - raza), min(inaltime, cy + raza + 1)):
            p = pixels[x, y]
            total[0] += p[0]
            total[1] += p[1]
            total[2] += p[2]
            n += 1
    if n == 0:
        return (0, 0, 0)
    return (total[0] / n, total[1] / n, total[2] / n)


def _luminozitate(culoare):
    return sum(culoare) / 3


def _e_acoperit(pixels, latime, inaltime):
    ''' Test de relief 3D: casuta acoperita e desenata ca un buton
    "ridicat" - colt stanga-sus luminos, colt dreapta-jos umbrit.
    O casuta deschisa e plata, cu margine subtire uniforma.
    '''
    tl = _medie_patch(pixels, 1, 1, 1, latime, inaltime)
    br = _medie_patch(pixels, latime - 2, inaltime - 2, 1, latime, inaltime)
    return _luminozitate(tl) - _luminozitate(br) > 35


def _forma_plina_si_rotunda(pixel_set, latime, inaltime):
    ''' Cat de "plina" si "rotunda" e o forma data ca set de coordonate
    (x,y). O mina e un bulgare plin (multi pixeli, densitate mare in
    propriul chenar). O cifra (ca 7) e o linie subtire (putini pixeli,
    densitate mica).
    Returneaza densitatea (0..1). Mina tipic > 0.4, cifra 7 tipic < 0.3.
    '''
    if not pixel_set:
        return 0.0
    xs = [p[0] for p in pixel_set]
    ys = [p[1] for p in pixel_set]
    bbox_w = max(xs) - min(xs) + 1
    bbox_h = max(ys) - min(ys) + 1
    bbox_area = bbox_w * bbox_h
    if bbox_area == 0:
        return 0.0
    return len(pixel_set) / bbox_area


def _numara_gri_mediu_interior(pixels, latime, inaltime, margine=3):
    ''' Cifra 8 e gri (128,128,128) - aceeasi nuanta ca umbra de pe
    marginea unei casute acoperite sau linia de grid a uneia deschise.
    Nu o putem distinge dupa culoare. O distingem dupa POZITIE: umbra si
    linia de grid traiesc doar langa margine (1-2px); interiorul ADANC
    al oricarei casute fara cifra 8 e mereu plin uniform cu fundalul
    (192,192,192). Deci daca gasim gri-mediu adanc in interior, unde n-ar
    trebui sa fie decat fundal plin, e semn de cifra 8.
    '''
    numar = 0
    for x in range(margine, latime - margine):
        for y in range(margine, inaltime - margine):
            r, g, b = pixels[x, y][:3]
            if max(r, g, b) - min(r, g, b) > 18:
                continue
            medie = (r + g + b) / 3
            if 95 <= medie <= 165:
                numar += 1
    return numar


def read_cell(cell_image):
    ''' Primeste o imagine PIL decupata a UNEI casute (aprox 13-18px,
    functioneaza cu putin padding in plus).
    Returneaza: 0-8, mg.CELL_COVERED, mg.CELL_MINE, mg.CELL_EXPLODED_MINE,
    sau None daca nu poate decide cu incredere (mai bine "nu stiu" decat
    o ghiceala gresita - vezi STOP_AT_UNKNOWN_CELL in bot.py).
    '''
    latime, inaltime = cell_image.size
    pixels = cell_image.convert("RGB").load()
    total_pixeli = latime * inaltime

    # 1. Fundal majoritar rosu -> mina explodata
    rosii = 0
    for x in range(latime):
        for y in range(inaltime):
            if _e_rosu(pixels[x, y]):
                rosii += 1
    if rosii / total_pixeli > 0.30:
        return mg.CELL_EXPLODED_MINE

    # 2. Colectam pixelii "de interes": colorati (posibila cifra) si
    # intunecati (posibila cifra 7 / mina), excluzand marginea (poate
    # avea artefacte de la casuta vecina)
    margine = 1
    pixeli_colorati = {}  # cifra -> lista de coordonate
    pixeli_intunecati = []
    pixeli_rosii = []

    for x in range(margine, latime - margine):
        for y in range(margine, inaltime - margine):
            p = pixels[x, y]
            if _e_intunecat(p):
                pixeli_intunecati.append((x, y))
                continue
            if _e_gri(p):
                continue
            if _e_rosu(p):
                pixeli_rosii.append((x, y))
            cifra = _cea_mai_apropiata_cifra(p)
            if cifra is not None:
                pixeli_colorati.setdefault(cifra, []).append((x, y))

    # 3. Daca avem destui pixeli rosii (dar nu destui cat sa fie
    # explozie) + niste pixeli negri (coada steagului) -> steag pus
    # (il tratam ca mina, la fel ca restul codului)
    if len(pixeli_rosii) >= 4 and len(pixeli_intunecati) >= 2:
        return mg.CELL_MINE

    # 4. Daca avem destui pixeli de o culoare de cifra -> aia e cifra
    if pixeli_colorati:
        cifra_dominanta = max(pixeli_colorati, key=lambda c: len(pixeli_colorati[c]))
        if len(pixeli_colorati[cifra_dominanta]) >= 3:
            return cifra_dominanta

    # 5. Pixeli negri semnificativi -> cifra 7 sau mina, dupa forma
    if len(pixeli_intunecati) >= 4:
        densitate = _forma_plina_si_rotunda(pixeli_intunecati, latime, inaltime)
        if densitate >= 0.40:
            return mg.CELL_MINE
        return 7

    # 5.5 Cifra 8 (gri, vezi explicatia functiei de mai sus)
    if latime > 7 and inaltime > 7:
        gri_mediu = _numara_gri_mediu_interior(pixels, latime, inaltime)
        if gri_mediu >= 3:
            return 8

    # 6. Niciun continut colorat/negru semnificativ -> acoperit sau 0
    if _e_acoperit(pixels, latime, inaltime):
        return mg.CELL_COVERED
    return 0
