import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS=60
win = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Black Hole Simulation")

C=299792458
G=6.67430e-11
SOLAR_MASS=1.98847e30

METERS_PER_PIXEL = 1e7

RAY_VELOCITY = C
RAY_SIZE=6

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


BG = pygame.transform.scale(pygame.image.load("background.jpg"),(WIDTH, HEIGHT))

class BlackHole:
    def __init__(self,x,y,mass):
        self.x=x
        self.y=y
        self.mass=mass
        self.r_s=self.schwarzschild_radius()
    def schwarzschild_radius(self):
        self.r_s=2*self.mass*G/(C**2)
        return self.r_s
    def draw(self):
        pygame.draw.circle(win,RED,(int(self.x),int(self.y)),int(self.r_s/METERS_PER_PIXEL))

class Ray:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.velocity = RAY_VELOCITY
    def move(self):
        self.x+=self.velocity/METERS_PER_PIXEL
    def draw(self):
        pygame.draw.rect(win,WHITE,(int(self.x),int(self.y),RAY_SIZE,RAY_SIZE))

def main():
    running = True
    clock = pygame.time.Clock()
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        bl = BlackHole(WIDTH//2, HEIGHT//2, 100000*SOLAR_MASS)
        ray = Ray()
        win.blit(BG, (0, 0))
        bl.draw()
        ray.draw()
        ray.move()
        pygame.display.update()
    
    pygame.quit()
    
if __name__ == "__main__":
    main()