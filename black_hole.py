import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS=60
win = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Black Hole Simulation")

G=6.67430e-11
SOLAR_MASS=1.98847e30

METERS_PER_PIXEL = 5*1e6
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
        # print(self.x,self.y)
        #max length of trail is 1000
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
    y_pos=[i for i in range(0,30)]
    for y in y_pos:
        rays.append(Ray(0,0,black_hole,(1.0,3.0+y*0.25)))

def create_ray_one(black_hole):
    rays.append(Ray(WIDTH//6,HEIGHT//5,black_hole,(1.0,3.0)))

def create_rays_horizontal(black_hole, y_step=10):
    for y in range(0, HEIGHT, y_step):
        rays.append(Ray(0, y, black_hole, (1.0, 0.0)))

def create_rays_fan(black_hole, origin_x=0, origin_y=None, count=36, spread=math.pi/2):
    oy = origin_y if origin_y is not None else HEIGHT // 2
    center_ang = math.atan2(black_hole.y - oy, black_hole.x - origin_x)
    for i in range(count):
        a = center_ang - spread/2 + i * (spread / max(1, count - 1))
        dx, dy = math.cos(a), math.sin(a)
        rays.append(Ray(origin_x, oy, black_hole, (dx, dy)))

def create_rays_radial(black_hole, count=72, radius=300):
    cx, cy = black_hole.x, black_hole.y
    for i in range(count):
        a = 2 * math.pi * i / count
        sx = cx + math.cos(a) * radius
        sy = cy + math.sin(a) * radius
        dir_x = -math.sin(a)
        dir_y = math.cos(a)
        rays.append(Ray(sx, sy, black_hole, (dir_x, dir_y)))

def geodesic(ray, rhs,r_s_m):
    
    dphi = max(min(ray.dphi, 1e6), -1e6)
    dr = ray.dr

    r_px = max(ray.r, 1e-6)
    r_m = r_px * METERS_PER_PIXEL

    term_m = (C_SI * C_SI * r_s_m) / (2.0 * r_m * r_m)

    term_px = term_m / METERS_PER_PIXEL

    radial_acc_px = ray.r * (dphi ** 2) - term_px

    angular_acc = -2.0 * dr * dphi / max(ray.r, 1e-6)

    # ray.d2r = radial_acc_px
    # ray.d2phi = angular_acc
    rhs.clear()
    rhs.extend([dr,dphi,radial_acc_px,angular_acc])

def add_state(a,b,factor,out):
    out.clear()
    out.extend([a[i]+factor*b[i] for i in range(4)])

def rk4_step(ray, black_hole, dlambda):
    if(ray.r < black_hole.r_px):
        return
    y0=[ray.r, ray.phi, ray.dr, ray.dphi]
    k1,k2,k3,k4,temp=[],[],[],[],[]

    geodesic(ray,k1, black_hole.r_si)
    add_state(y0,k1,dlambda/2.0,temp)
    r2=Ray(0, 0, black_hole, (0, 0))
    r2.r, r2.phi, r2.dr, r2.dphi = temp
    geodesic(r2,k2, black_hole.r_si)

    add_state(y0,k2,dlambda/2.0,temp)
    r3=Ray(0, 0, black_hole, (0, 0))
    r3.r, r3.phi, r3.dr, r3.dphi = temp
    geodesic(r3,k3, black_hole.r_si)

    add_state(y0,k3,dlambda,temp)
    r4=Ray(0, 0, black_hole, (0, 0))
    r4.r, r4.phi, r4.dr, r4.dphi = temp
    geodesic(r4,k4, black_hole.r_si)

    ray.r+=(dlambda/6.0)*(k1[0]+2.0*k2[0]+2.0*k3[0]+k4[0])
    ray.phi+=(dlambda/6.0)*(k1[1]+2.0*k2[1]+2.0*k3[1]+k4[1])
    ray.dr+=(dlambda/6.0)*(k1[2]+2.0*k2[2]+2.0*k3[2]+k4[2])
    ray.dphi+=(dlambda/6.0)*(k1[3]+2.0*k2[3]+2.0*k3[3]+k4[3])

def main():
    bl = BlackHole(WIDTH//2, HEIGHT//2, 200000*SOLAR_MASS)
    create_ray_one(bl)
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
            rk4_step(ray, bl, 1e-2)
            ray.move(bl,0)
            ray.draw()
            
            off_screen = ray.x>WIDTH or ray.x<0 or ray.y<0 or ray.y>HEIGHT
            if off_screen:
                # print("off_screen")
                rays.remove(ray)
        pygame.display.update()
    
    pygame.quit()
    
if __name__ == "__main__":
    main()