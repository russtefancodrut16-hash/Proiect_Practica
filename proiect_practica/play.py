
import time

import pyautogui

import minesweeper_game as mg
from bot import Bot


def main():
    print("Ai 5 secunde sa aduci jocul de Minesweeper pe ecran ")
    time.sleep(5)
    print()

    bot = Bot()

    print("Caut tabla...")
    gasit, mesaj = bot.gaseste_joc()
    print(f"  {mesaj}")
    if not gasit:
        print("\nVerifica: jocul e vizibil, la scala 100%, skin clasic (gri).")
        return

    print("\nJoc...\n")
    rezultat = bot.joaca_un_joc()

    print()
    if rezultat == mg.STATUS_WON:
        print("=" * 40)
        print("AM CASTIGAT!")
        print("=" * 40)
    else:
        print("=" * 40)
        print("Am murit. :(")
        print("Daca a aparut mesajul 'ATENTIE: ... marcate contradictoriu' "
              "mai sus, acolo e cauza probabila - o casuta a fost citita "
              "gresit undeva pe tabla.")
        print("=" * 40)


if __name__ == "__main__":
    main()
