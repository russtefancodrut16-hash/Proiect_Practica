import pyautogui
import keyboard
import time
import random
import logging
import sys
import os
from PIL import ImageDraw # NOU: Modul pentru a desena patrate de detectie

# Configurare sistem de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("bot_activity.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class VisionBot:
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.is_running = False
        
        director_curent = os.path.dirname(os.path.abspath(__file__))
        self.target_image_path = os.path.join(director_curent, "assets", "tinta.png.png") # Am lasat varianta cu .png.png care iti mergea
        
        # O setare noua care salveaza dovezile vizuale
        self.salveaza_dovezi_vizuale = True 
        
        if not os.path.exists(self.target_image_path):
            # In caz ca l-ai redenumit inapoi in tinta.png, incercam si asa
            self.target_image_path = os.path.join(director_curent, "assets", "tinta.png")
            if not os.path.exists(self.target_image_path):
                logging.error(f"Fisierul tinta NU exista in folderul assets!")
                sys.exit(1)
            
        logging.info("VisionBot initializat (cu modulul AI Visual Debugging activat).")
        self._afiseaza_meniu()

    def _afiseaza_meniu(self):
        print("\n" + "="*50)
        print("🤖 VISION BOT AUTO-PLAYER (Computer Vision v2.0)")
        print("="*50)
        print("[+] Sistem vizual de marcare a tintelor (Red Bounding Box)")
        print("[E] -> START / PAUZA BOT")
        print("[Q] -> KILL-SWITCH (Opreste de urgenta)")
        print("="*50 + "\n")

    def toggle_bot(self):
        self.is_running = not self.is_running
        if self.is_running:
            logging.info("STATUS: Bot ACTIVAT. Incep scanarea inteligenta a ecranului...")
        else:
            logging.info("STATUS: Bot PAUZAT.")
        time.sleep(0.3) 

    def executa_ciclu(self):
        try:
            # Folosim un grad de incredere de 80% (confidence)
            locatie_tinta = pyautogui.locateOnScreen(self.target_image_path, confidence=0.8)
            
            if locatie_tinta is not None:
                logging.info("TINTA DETECTATA pe ecran!")
                
                # --- NOU: DOVADA VIZUALA (Visual Debugging) ---
                if self.salveaza_dovezi_vizuale:
                    # Face un screenshot general
                    captura = pyautogui.screenshot()
                    desen = ImageDraw.Draw(captura)
                    
                    # Deseneaza un patrat rosu gros (Bounding Box) in jurul tintei gasite
                    margine_stanga = locatie_tinta.left
                    margine_sus = locatie_tinta.top
                    margine_dreapta = locatie_tinta.left + locatie_tinta.width
                    margine_jos = locatie_tinta.top + locatie_tinta.height
                    
                    desen.rectangle(
                        [margine_stanga, margine_sus, margine_dreapta, margine_jos],
                        outline="red", width=5
                    )
                    
                    # Salveaza poza in folderul proiectului
                    cale_salvare = os.path.join(os.path.dirname(self.target_image_path), "..", "debug_vision.png")
                    captura.save(cale_salvare)
                    logging.info(f"Dovada vizuala (AI Bounding Box) a fost salvata: debug_vision.png")
                # ---------------------------------------------
                
                # Calculam centrul tintei gasite
                centru_x, centru_y = pyautogui.center(locatie_tinta)
                
                # Delay uman inainte de a reactiona
                time.sleep(random.uniform(0.1, 0.3))
                
                # Miscare organica a mouse-ului
                # timp_miscare = random.uniform(0.2, 0.5)
                # pyautogui.moveTo(centru_x, centru_y, duration=timp_miscare, tween=pyautogui.easeInOutQuad)
                
                # logging.info(f"Executare actiune click la coordonatele: ({centru_x}, {centru_y})")
                # pyautogui.click()
                logging.info(f"Executare actiune INSTANTA la coordonatele: ({centru_x}, {centru_y})")
                pyautogui.click(centru_x, centru_y)
                
                # Delay uman dupa click
                time.sleep(random.uniform(0.5, 1.5))
                
                # Oprim temporar bot-ul ca sa poti admira poza (poti sterge linia asta daca vrei sa dea click non-stop)
                self.is_running = False
                logging.info("Bot-ul a fost pus pe pauza automat dupa reusita ca sa poti verifica poza de debug.")
            else:
                time.sleep(0.5)
                
        except Exception as e:
            logging.error(f"Eroare procesare vizuala: {e}")
            time.sleep(1)

    def run(self):
        try:
            while True:
                if keyboard.is_pressed('q'):
                    logging.info("Kill-Switch apasat. Iesire de urgenta...")
                    break
                    
                if keyboard.is_pressed('e'):
                    self.toggle_bot()
                    
                if self.is_running:
                    self.executa_ciclu()
                    
        except pyautogui.FailSafeException:
            logging.error("CRITICAL ERROR: Mecanismul Fail-Safe a fost declansat!")