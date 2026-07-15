from vision_bot import VisionBot
import time

def main():
    print("Incarcare module AI si Computer Vision...")
    time.sleep(1) 
    
    # Instantiem obiectul bot-ului
    bot = VisionBot()
    
    # Pornim bucla continua
    bot.run()

if __name__ == "__main__":
    main()