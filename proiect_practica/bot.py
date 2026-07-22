

import time

import pyautogui
import numpy as np

import minesweeper_game as mg
import minesweeper_solver as ms
from grid_finder import gaseste_tabla
from screen_reader import read_cell



OPRESTE_LA_CASUTA_NECUNOSCUTA = False


class Bot:
    def __init__(self):
        self.tabla = None
        self.solver = None

    def gaseste_joc(self):
        ''' Cauta tabla pe ecran. Returneaza (True/False, mesaj). '''
        screenshot = pyautogui.screenshot()
        tabla, mesaj = gaseste_tabla(screenshot)
        if tabla is None:
            return False, mesaj

        self.tabla = tabla
        settings = mg.GameSettings((tabla.latime, tabla.inaltime), tabla.mine)
        self.solver = ms.MinesweeperSolver(settings)
        return True, mesaj

    def citeste_tabla(self, screenshot=None, padding=2):
        ''' Citeste continutul curent al tablei de pe ecran.
        Returneaza un numpy array (latime x inaltime).
        '''
        if screenshot is None:
            screenshot = pyautogui.screenshot()

        field = np.zeros((self.tabla.latime, self.tabla.inaltime), dtype=int)
        necunoscute = []

        for col in range(self.tabla.latime):
            for rand in range(self.tabla.inaltime):
                left, top, right, bottom = self.tabla.coordonate[col, rand]
                cutie = (left - padding, top - padding, right + padding, bottom + padding)
                imagine_casuta = screenshot.crop(cutie)
                valoare = read_cell(imagine_casuta)

                if valoare is None:
                    necunoscute.append((col, rand))
                    valoare = 0
                    if OPRESTE_LA_CASUTA_NECUNOSCUTA:
                        cale = f"necunoscut-{col}-{rand}.png"
                        imagine_casuta.save(cale)
                        raise ValueError(f"Nu pot citi casuta ({col},{rand}), salvata ca {cale}")

                field[col, rand] = valoare

        if necunoscute:
            print(f"  (Atentie: {len(necunoscute)} casuta(e) necunoscute, "
                  f"tratate ca ignorabile: {necunoscute[:5]}"
                  f"{'...' if len(necunoscute) > 5 else ''})")

        return field, screenshot

    def e_mort(self, field):
        return bool((field == mg.CELL_EXPLODED_MINE).any())

    def a_castigat(self, field):
        return not bool((field == mg.CELL_COVERED).any())

    def executa_clickuri(self, safe, mines):
        ''' Executa mutarea completa: intai steagurile (cu confirmare si
        reincercare - vezi confirma_steaguri), ABIA APOI deschiderile.
        Ordinea asta conteaza: nu vrem sa deschidem o casuta langa o
        mina care s-ar putea sa nu fi fost marcata cu adevarat inca.
        '''
        if mines:
            for coord in mines:
                left, top, right, bottom = self.tabla.coordonate[coord]
                x = (left + right) // 2
                y = (top + bottom) // 2
                pyautogui.click(x, y, button="right")
                time.sleep(0.05)
            self.confirma_steaguri(mines)

        if safe:
            for coord in safe:
                left, top, right, bottom = self.tabla.coordonate[coord]
                x = (left + right) // 2
                y = (top + bottom) // 2
                pyautogui.click(x, y, button="left")
                time.sleep(0.05)

        pyautogui.moveTo(10, 10)

    def confirma_steaguri(self, mines, incercari=3):
        ''' Dupa ce marcam niste casute ca mine (click dreapta), verificam
        ca steagul chiar a aparut pe ecran, si reincercam daca nu.

        De ce: un click dreapta care nu ajunge la timp la joc (input
        pierdut) lasa o mina reala NEMARCATA. Solverul, la mutarea
        urmatoare, nu mai are niciun motiv sa banuiasca acea casuta -
        nu mai apare in nicio lista - si daca e prinsa intr-o cascada
        de zerouri, explodeaza fara avertisment (o mina cu steag nu e
        NICIODATA deschisa automat de o cascada - deci daca explodeaza,
        aproape sigur steagul nu s-a pus cu adevarat).
        '''
        if not mines:
            return

        de_reincercat = list(mines)
        for incercare in range(incercari):
            if not de_reincercat:
                return

            time.sleep(0.1)
            screenshot = pyautogui.screenshot()
            inca_nemarcate = []
            for coord in de_reincercat:
                left, top, right, bottom = self.tabla.coordonate[coord]
                cutie = (left - 2, top - 2, right + 2, bottom + 2)
                valoare = read_cell(screenshot.crop(cutie))
                if valoare != mg.CELL_MINE:
                    inca_nemarcate.append(coord)

            if not inca_nemarcate:
                return

            if incercare < incercari - 1:
                print(f"  (Steag(uri) {inca_nemarcate} nu au aparut, reincerc...)")
            for coord in inca_nemarcate:
                left, top, right, bottom = self.tabla.coordonate[coord]
                x = (left + right) // 2
                y = (top + bottom) // 2
                pyautogui.click(x, y, button="right")
                time.sleep(0.08)
            de_reincercat = inca_nemarcate

        if de_reincercat:
            print(f"  ATENTIE: {de_reincercat} tot nu au fost marcate dupa "
                  f"{incercari} incercari - posibil mina reala nemarcata pe tabla!")

    def muta(self):
        ''' Citeste tabla, cere solverului o mutare, o executa.
        Returneaza mg.STATUS_ALIVE / STATUS_DEAD / STATUS_WON.
        '''
        field, screenshot = self.citeste_tabla()

        if self.e_mort(field):
            return mg.STATUS_DEAD
        if self.a_castigat(field):
            return mg.STATUS_WON

        safe, mines = self.solver.solve(field)

        # Plasa de siguranta: nicio casuta nu se deschide (click stanga)
        # daca a fost marcata SI ca mina in aceeasi mutare, sau daca
        # tabla arata deja ca fiind mina acolo. In teorie nu ar trebui
        # sa se intample daca tabla a fost citita corect - daca se
        # intampla, e semn ca ceva a fost citit gresit undeva, nu o
        # eroare de logica a solverului.
        if safe:
            suspecte = set(safe) & set(mines or [])
            for coord in safe:
                if field[coord] == mg.CELL_MINE:
                    suspecte.add(coord)
            if suspecte:
                print(f"  ATENTIE: {suspecte} marcate contradictoriu, nu dau click pe ele.")
                safe = [c for c in safe if c not in suspecte]

        print(f"  Metoda: {self.solver.last_move_info[0]}"
              + (f", sansa mina: {self.solver.last_move_info[2]:.1%}"
                 if self.solver.last_move_info[2] is not None else ""))
        if safe:
            print(f"  Click stanga: {safe}")
        if mines:
            print(f"  Click dreapta (steag): {mines}")

        self.executa_clickuri(safe, mines)
        time.sleep(0.25)
        return mg.STATUS_ALIVE

    def joaca_un_joc(self):
        ''' Joaca pana la victorie sau infrangere. Returneaza statusul final. '''
        while True:
            rezultat = self.muta()
            if rezultat != mg.STATUS_ALIVE:
                return rezultat