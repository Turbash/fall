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
PLANET = pygame.transform.scale(pygame.image.load("planet.png"),(PLANET_SIZE*2,PLANET_SIZE*2))

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def main():
    pass

if __name__ == ""__main__":
    main()