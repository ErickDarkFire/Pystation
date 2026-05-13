import os
import pygame
from core.game import Game


def before_all(context):
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.init()
    pygame.display.set_mode((800, 600))


def before_scenario(context, scenario):
    context.game = Game()
    context.game.shoe.cards.clear()


def after_all(context):
    pygame.quit()
