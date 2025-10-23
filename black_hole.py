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
    def __init__(self,x,y,black_hole,dir):
        self.x = x
        self.y = y
        self.velocity = C/METERS_PER_PIXEL
        self.trail = [(x,y)]
        self.dir=dir
        self.r = math.hypot(self.x - black_hole.x, self.y - black_hole.y)
        self.phi = math.atan2(self.y - black_hole.y, self.x - black_hole.x)
        self.dr = C*math.cos(self.phi)+self.dir[1]*math.sin(self.phi)
        self.dphi=(-C*math.sin(self.phi)+self.dir[1]*math.cos(self.phi))/self.r
        self.d2r = 0
        self.d2phi = 0

    def move(self,black_hole, dlambda):
        if self.r < black_hole.r_s / METERS_PER_PIXEL:
            # Ray has crossed the event horizon, stop updating
            return
        
        self.dr+=self.d2r*dlambda
        self.dphi+=self.d2phi*dlambda
        self.r+=self.dr*dlambda
        self.phi+=self.dphi*dlambda
        self.x += math.cos(self.phi)*self.r
        self.y += math.sin(self.phi)*self.r
        #max length of trail is 100

        if len(self.trail)>1000:
            self.trail.pop(0)
        self.trail.append((self.x,self.y))

    def draw(self):
        pygame.draw.line(win,WHITE,(int(self.x),int(self.y)),(int(self.x),int(self.y)))
        for i in range(len(self.trail)-1):
            #brightness recudes with trail age
            brightness = 0+int((i/len(self.trail))*255)
            color = (brightness, brightness, brightness)
            pygame.draw.line(win, color, (int(self.trail[i][0]), int(self.trail[i][1])), (int(self.trail[i][0]), int(self.trail[i][1])))

def create_rays(black_hole):
    y_pos=[i for i in range(0,HEIGHT,10)]
    for y in y_pos:
        rays.append(Ray(WIDTH//3,y,black_hole,(1,0)))

def geodesic(ray,r_s):
    ray.dr+=ray.r*ray.dphi*ray.dphi-(C*C*r_s)/(2.0*ray.r*ray.r)
    ray.dphi=-2.0*ray.dr*ray.dphi/ray.r

def main():
    bl = BlackHole(WIDTH//2, HEIGHT//2, 1000000*SOLAR_MASS)
    create_rays(bl)
    running = True
    clock = pygame.time.Clock()
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.blit(BG, (0, 0))
        bl.draw()

        for ray in rays[:]:
            geodesic(ray, bl.r_s)
            ray.draw()
            ray.move(bl,1e-1)

            off_screen = ray.x>WIDTH or ray.x<0 or ray.y<0 or ray.y>HEIGHT
            if off_screen:
                print("off_screen")
                rays.remove(ray)
        pygame.display.update()
    
    pygame.quit()
    
if __name__ == "__main__":
    main()