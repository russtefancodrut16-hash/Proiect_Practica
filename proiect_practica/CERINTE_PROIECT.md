Cerințe Proiect: Dezvoltare Bot de Automatizare  în Python

1. Descriere Generală și Obiectiv
Obiectivul acestui proiect este dezvoltarea unui bot autonom scris în Python, capabil să joace un joc (ex: Tic-Tac-Toe, Minesweeper, jocuri de tip Idle/Clicker) fără intervenție umană. Bot-ul va folosi tehnici de procesare vizuală  pentru a „citi” starea jocului de pe ecran, va calcula următoarea mutare pe baza unui algoritm predefinit și va simula input-ul fizic pentru a executa mutarea.

2. Stiva Tehnologică 
Limbaj de programare: Python 3.x
Interacțiune periferice: `pyautogui` (pentru controlul cursorului și simularea click-urilor).
Procesare de imagine: `Pillow`  sau `OpenCV`  (pentru a recunoaște elementele grafice, butoanele sau obstacolele de pe ecran).
Utilitare: `time`, `random` (pentru gestionarea pauzelor și simularea comportamentului uman), `keyboard` (pentru setarea unor scurtături de întrerupere).

3. Arhitectura și Fluxul de Execuție 
Bot-ul va funcționa într-o buclă continuă (`while loop`), respectând următorii 4 pași fundamentali:

1. Calibrarea și Recunoașterea : Identificarea zonei de lucru pe ecran .
    Preluarea unui 'screenshot' al zonei respective pentru a evalua starea curentă a jocului.
2. Extragerea Datelor : Compararea pixelilor sau identificarea imaginilor predefinite (ex: căutarea unui buton de "Play" folosind funcția `pyautogui.locateOnScreen()`).
3. Logica de Decizie : Aplicarea regulilor jocului asupra datelor extrase pentru a determina mutarea optimă.
4. Execuția Mutării : Deplasarea cursorului la coordonatele calculate și simularea click-ului.

4. Cerințe de Siguranță și Optimizare 
Deoarece scripturile de automatizare pot prelua controlul total asupra mouse-ului, proiectul va include obligatoriu următoarele mecanisme de siguranță:
Fail-Safe Activ: Activarea caracteristicii `pyautogui.FAILSAFE = True` (oprirea forțată a scriptului dacă utilizatorul trage brusc mouse-ul într-unul din cele 4 colțuri ale ecranului).
Kill-Switch : Alocarea unei taste globale (ex: tasta `Q` sau `Esc`) care, la apăsare, termină instantaneu procesul Python.
Comportament Uman: Introducerea unor timpi de întârziere (delays) aleatorii între mișcări folosind `random.uniform()`, pentru a evita detecția bot-ului și pentru a nu bloca sistemul de operare.

 5. Livrabile
Pentru finalizarea cu succes a proiectului, repository-ul de GitHub va conține:
 Fișierul principal cu codul sursă .
Un fișier `requirements.txt` ce va conține dependențele necesare (`pip install -r requirements.txt`).
 Un folder `/assets` în care se vor afla imaginile de referință (ex: poze mici cu butoanele pe care bot-ul trebuie să le recunoască pe ecran).
