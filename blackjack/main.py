from core.game import Game

if __name__ == "__main__":
    try:
        blackjack_game = Game()
        blackjack_game.run()
    except Exception as e:
        print(f"Error: {e}")
        import pygame

        pygame.quit()
