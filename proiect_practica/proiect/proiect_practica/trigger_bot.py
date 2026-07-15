import pyautogui
import keyboard
import time
import logging
import sys
import math
import random # NOU: Importam modulul random pentru umanizarea bot-ului

# CONFIGURARE SISTEM DE LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("bot_activity.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ValorantTriggerBot:
    """
    Clasa principala pentru TriggerBot. 
    Include: Toleranta matematica la culori + Mecanisme de umanizare (Anti-Cheat Bypass).
    """
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.is_running = False
        self.target_color = None
        self.target_x = 0
        self.target_y = 0
        
        # PARAMETRI DE CONFIGURARE
        self.toleranta_culoare = 30 
        
        # PARAMETRI DE UMANIZARE (Milisecunde adaugate aleatoriu)
        self.reactie_min = 0.02 # Timp minim de reactie (20ms)
        self.reactie_max = 0.08 # Timp maxim de reactie (80ms)
        
        logging.info("Sistemul TriggerBot (V3 - Stealth & Humanized) a fost initializat.")
        self._afiseaza_meniu()

    def _afiseaza_meniu(self):
        print("\n" + "="*50)
        print("🤖 INTERFATA TRIGGER BOT (V3 - STEALTH MODE)")
        print("="*50)
        print("[+] Toleranta culori activa (Anti-Flicker)")
        print("[+] Timp de reactie randomizat (Anti-Cheat Bypass)")
        print("-" * 50)
        print("[S] -> START / PAUZA")
        print("[Q] -> OPRESTE PROGRAMUL")
        print("="*50 + "\n")

    def toggle_bot(self):
        self.is_running = not self.is_running
        
        if self.is_running:
            self.target_x, self.target_y = pyautogui.position()
            self.target_color = pyautogui.pixel(self.target_x, self.target_y)
            logging.info(f"CALIBRARE: Coordonate ({self.target_x}, {self.target_y}) - RGB: {self.target_color}")
            logging.info("STATUS: Bot ACTIVAT in modul Stealth.")
        else:
            logging.info("STATUS: Bot PAUZAT.")
        
        time.sleep(0.3) 

    def _calcul_distanta_culori(self, c1, c2):
        delta_r = c1[0] - c2[0]
        delta_g = c1[1] - c2[1]
        delta_b = c1[2] - c2[2]
        return math.sqrt(delta_r**2 + delta_g**2 + delta_b**2)

    def executa_actiune(self):
        current_color = pyautogui.pixel(self.target_x, self.target_y)
        diferenta = self._calcul_distanta_culori(self.target_color, current_color)
        
        if diferenta > self.toleranta_culoare:
            logging.warning(f"DETECTIE VIZUALA! (Variatie RGB: {diferenta:.2f})")
            
            # 1. MECANISM ANTI-CHEAT: Asteptam un timp aleatoriu (simulam reflexul uman)
            human_reaction = random.uniform(self.reactie_min, self.reactie_max)
            logging.info(f"Stealth: Simulare reflex uman... ({human_reaction:.3f} secunde)")
            time.sleep(human_reaction)
            
            # 2. Executia actiunii
            logging.info("ACTIUNE: Click automat!")
            pyautogui.click(self.target_x, self.target_y)
            
            # 3. MECANISM ANTI-CHEAT: Pauza aleatorie dupa click
            human_cooldown = random.uniform(0.3, 0.6)
            time.sleep(human_cooldown) 
            
            # Recalibrare automata
            self.target_color = pyautogui.pixel(self.target_x, self.target_y)
            logging.info("Sistem recalibrat. Monitorizare reluata...")

    def run(self):
        try:
            while True:
                if keyboard.is_pressed('q'):
                    logging.info("Sistem oprit de utilizator. La revedere!")
                    break
                if keyboard.is_pressed('s'):
                    self.toggle_bot()
                if self.is_running:
                    self.executa_actiune()
                    
        except pyautogui.FailSafeException:
            logging.error("CRITICAL ERROR: Fail-Safe declansat!")