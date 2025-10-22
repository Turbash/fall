import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Gravitational Slingshot Simulation")

PLANET_MASS = 100
SHIP_MASS = 5
G = 5
FPS = 60
PLANET_SIZE=50
OBJ_SIZE=5
VEL_SCALE=100

BG = pygame.transform.scale(pygame.image.load("background.jpg"),(WIDTH, HEIGHT))
PLANET = pygame.transform.scale(pygame.image.load("jupiter.png"),(PLANET_SIZE*2,PLANET_SIZE*2))

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def main():
    running = True
    clock = pygame.time.Clock()
    temp_obj_pos = None

    while(running):
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                temp_obj_pos = pygame.mouse.get_pos()
                

        win.blit(BG, (0, 0))

        if temp_obj_pos is not None:
            pygame.draw.circle(win, RED, temp_obj_pos, OBJ_SIZE)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()