from datetime import datetime
import pygame
import theme as th
import random


pygame.init()
screen = pygame.display.set_mode((1300, 800))


class Game:
    def show_menu(self):
        screen.fill((100, 100, 100))
    def show_game(self):
        screen.fill((200, 200, 200))
        
running = True
main_menu = True
main_game = False
game = Game()
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Закрытие окна
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                main_menu = not main_menu
                main_game = not main_game
    if main_menu:
        game.show_menu()
    elif main_game:
        game.show_game()
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
    
