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

METERS_PER_PIXEL = 1e8

RAY_SIZE=2

rays=[]

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
        # Show radius on top of black hole
        # font = pygame.font.SysFont("Arial", 24)
        # text = font.render(f"radius: {self.r_s:.16f} metres", True, WHITE)
        # win.blit(text, (int(self.x), int(self.y)))

class Ray:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.velocity = C/METERS_PER_PIXEL
        self.trail = [(x,y)]
    def move(self):
        self.x += self.velocity
        #max length of trail is 100
        if len(self.trail)>100:
            self.trail.pop(0)
        self.trail.append((self.x,self.y))
    def draw(self):
        pygame.draw.rect(win,WHITE,(int(self.x),int(self.y),RAY_SIZE,RAY_SIZE))
        for i in range(len(self.trail)-1):
            #brightness recudes with trail age
            brightness = 0+int((i/len(self.trail))*255)
            color = (brightness, brightness, brightness)
            pygame.draw.rect(win, color, (int(self.trail[i][0]), int(self.trail[i][1]), RAY_SIZE, RAY_SIZE))

def create_rays():
    y_pos=[i for i in range(0,HEIGHT,RAY_SIZE*4)]
    for y in y_pos:
        rays.append(Ray(0,y))

def main():
    create_rays()
    running = True
    clock = pygame.time.Clock()
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        bl = BlackHole(WIDTH//2, HEIGHT//2, 1000000*SOLAR_MASS)
        win.blit(BG, (0, 0))
        bl.draw()
        for ray in rays[:]:
            ray.draw()
            ray.move()

            off_screen = ray.x>WIDTH
            if off_screen:
                rays.remove(ray)
        pygame.display.update()
    
    pygame.quit()
    
if __name__ == "__main__":
    main()