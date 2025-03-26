import traceback
from game import Game
import sys
import os

def main():
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nGame stop by you .")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        
        input("\nAn error Enter to exit...")
    finally:
        try:
            import pygame
            pygame.quit()
        except:
            pass
        
        sys.exit(0)

if __name__ == "__main__":
    main()
