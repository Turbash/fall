import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS=60
win = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Black Hole Simulation")

G=6.67430e-11
SOLAR_MASS=1.98847e30

METERS_PER_PIXEL = 5*1e7
C_PX=299792458.0/METERS_PER_PIXEL
C_SI=299792458.0

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
        self.r_si=self.schwarzschild_radius()
        self.r_px=self.r_si/METERS_PER_PIXEL

    def schwarzschild_radius(self):
        r_s=2*self.mass*G/(C_SI**2)
        return r_s    
    
    def draw(self):
        pygame.draw.circle(win,RED,(int(self.x),int(self.y)),int(self.r_px))
        # Show radius on top of black hole
        # font = pygame.font.SysFont("Arial", 24)
        # text = font.render(f"radius: {self.r_s:.16f} metres", True, WHITE)
        # win.blit(text, (int(self.x), int(self.y)))

class Ray:
    def __init__(self,x,y,black_hole,dir):
        self.x = x
        self.y = y
        self.trail = [(x,y)]
        self.dir=dir
        self.r = math.hypot(self.x - black_hole.x, self.y - black_hole.y)
        self.phi = math.atan2(self.y - black_hole.y, self.x - black_hole.x)
        self.dr = C_PX*math.cos(self.phi)+self.dir[1]*math.sin(self.phi)
        self.dphi=(-C_PX*math.sin(self.phi)+self.dir[1]*math.cos(self.phi))/self.r
        self.d2r = 0
        self.d2phi = 0

    def move(self,black_hole, dlambda):
        if self.r < black_hole.r_px:
            # Ray has crossed the event horizon, stop updating
            return
        
        self.dr+=self.d2r*dlambda
        self.dphi+=self.d2phi*dlambda
        self.r+=self.dr*dlambda
        self.phi+=self.dphi*dlambda
        self.x = black_hole.x + math.cos(self.phi)*self.r
        self.y = black_hole.y + math.sin(self.phi)*self.r
        print(self.x,self.y)
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
    y_pos=[i for i in range(0,HEIGHT,100)]
    for y in y_pos:
        rays.append(Ray(0,y,black_hole,(1.0,0.0)))

def geodesic(ray, r_s_m):
    r_px = max(ray.r, 1e-6)
    r_m = r_px * METERS_PER_PIXEL

    term_m = (C_SI * C_SI * r_s_m) / (2.0 * r_m * r_m)

    term_px = term_m / METERS_PER_PIXEL

    radial_acc_px = ray.r * (ray.dphi ** 2) - term_px

    angular_acc = -2.0 * ray.dr * ray.dphi / max(ray.r, 1e-6)

    ray.d2r = radial_acc_px
    ray.d2phi = angular_acc

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
            geodesic(ray, bl.r_si)
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