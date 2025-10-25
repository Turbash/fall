import pygame
import math
import pygame_gui

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Black Hole Simulation")
pygame.mixer.init()

pygame.mixer.music.load("black_hole_ambience.mp3")
pygame.mixer.music.play(-1)

BG_INTERSTELLAR = pygame.transform.scale(pygame.image.load("splash1.jpg"), (WIDTH, HEIGHT))
BG = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))

G = 6.67430e-11
SOLAR_MASS = 1.98847e30
C_SI = 299792458.0

INTERSTELLAR_MASS_KG = 39000 * SOLAR_MASS
INTERSTELLAR_METERS_PER_PIXEL = 1e6

CUSTOM_MASS_KG = 1000 * SOLAR_MASS
CUSTOM_METERS_PER_PIXEL = 1e5

CURRENT_MASS_KG = INTERSTELLAR_MASS_KG
METERS_PER_PIXEL = INTERSTELLAR_METERS_PER_PIXEL
C_PX = C_SI / METERS_PER_PIXEL

rays = []
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

state = "main_menu"  
sim_mode = "interstellar" 
manager = pygame_gui.UIManager((WIDTH, HEIGHT),'theme.json')

main_menu_buttons = []
settings_ui_elements = []

settings_mass_slider = None
settings_mpp_slider = None
settings_mass_label = None
settings_mpp_label = None

def create_main_menu():
    global main_menu_elements
    b_y_1 = 150
    b_y_2 = b_y_1 + 120
    b_y_3 = b_y_2 + 120
    
    main_menu_elements = [
        pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, b_y_1), (300, 50)),
                                     text='Interstellar Mode',
                                     manager=manager),
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, b_y_1 + 50), (300, 20)),
                                    text="Fixed simulation. Black hole is invisible.",
                                    manager=manager,
                                    object_id="#info_label"),

        pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, b_y_2), (300, 50)),
                                     text='Custom Mode',
                                     manager=manager),
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, b_y_2 + 50), (300, 20)),
                                    text="Custom parameters. Black hole is visible.",
                                    manager=manager,
                                    object_id="#info_label"),
        
        pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, b_y_3), (300, 50)),
                                     text='Settings (for Custom Mode)',
                                     manager=manager),
        
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((200, 100), (400, 20)),
                                    text="In simulation: Press [ESC] to return to menu.",
                                    manager=manager,
                                    object_id="#info_label"),
    ]

def destroy_main_menu():
    for el in main_menu_elements:
        el.kill()
    main_menu_elements.clear()

def create_settings_menu():
    global settings_ui_elements, settings_mass_slider, settings_mpp_slider, settings_mass_label, settings_mpp_label
    global CUSTOM_MASS_KG, CUSTOM_METERS_PER_PIXEL

    current_mass_mult = CUSTOM_MASS_KG / SOLAR_MASS
    current_mpp = CUSTOM_METERS_PER_PIXEL

    settings_mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 150), (300, 40)),
                                                     text=f'Custom Mass Mult: {current_mass_mult:.0f}',
                                                     manager=manager)
    
    settings_mass_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((250, 180), (300, 40)),
                                                                 start_value=current_mass_mult,
                                                                 value_range=(1000, 100000),
                                                                 manager=manager)

    settings_mpp_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 250), (300, 40)),
                                                    text=f'Custom Meters/Pixel: {current_mpp:.2e}',
                                                    manager=manager)
    
    settings_mpp_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((250, 280), (300, 40)),
                                                                start_value=current_mpp,
                                                                value_range=(1e5, 1e7),
                                                                manager=manager)

    back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 400), (200, 50)),
                                              text='Back to Menu',
                                              manager=manager)
    
    info_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 100), (300, 20)),
                                             text="Press [ESC] to return to menu.",
                                             manager=manager,
                                             object_id="#info_label")

    settings_ui_elements = [settings_mass_label, settings_mass_slider, settings_mpp_label, settings_mpp_slider, back_button, info_label]

def destroy_settings_menu():
    for el in settings_ui_elements:
        el.kill()
    settings_ui_elements.clear()

class BlackHole:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
        self.r_si = self.schwarzschild_radius()
        self.r_px = self.r_si / METERS_PER_PIXEL 

    def schwarzschild_radius(self):
        r_s = 2 * self.mass * G / (C_SI ** 2)
        r_s=min(r_s,500*METERS_PER_PIXEL)
        r_s=max(r_s,2*METERS_PER_PIXEL)
        return r_s

    def draw(self):
        pygame.draw.circle(win, RED, (int(self.x), int(self.y)), int(self.r_px))

class Ray:
    def __init__(self, x, y, black_hole, dir):
        self.x = x
        self.y = y
        self.trail = [(x, y)]
        self.dir = dir
        self.r = math.hypot(self.x - black_hole.x, self.y - black_hole.y)
        self.phi = math.atan2(self.y - black_hole.y, self.x - black_hole.x)
        dx, dy = self.dir
        mag = math.hypot(dx, dy) or 1.0
        ux, uy = dx / mag, dy / mag
        self.dr = C_PX * (ux * math.cos(self.phi) + uy * math.sin(self.phi)) 
        self.dphi = (C_PX * (-ux * math.sin(self.phi) + uy * math.cos(self.phi))) / max(self.r, 1e-6)
        self.d2r = 0
        self.d2phi = 0

    def move(self, black_hole, dlambda):
        if self.r < black_hole.r_px:
            return

        self.dr += self.d2r * dlambda
        self.dphi += self.d2phi * dlambda
        self.r += self.dr * dlambda
        self.phi += self.dphi * dlambda
        self.x = black_hole.x + math.cos(self.phi) * self.r
        self.y = black_hole.y + math.sin(self.phi) * self.r
        
        if len(self.trail) > 1000: 
            self.trail.pop(0)
        self.trail.append((self.x, self.y))

    def draw(self):
        if self.r > 0: 
            pygame.draw.circle(win, WHITE, (int(self.x), int(self.y)), 1)
        
        if len(self.trail) > 1:
            points = [(int(p[0]), int(p[1])) for p in self.trail]
            pygame.draw.aalines(win, WHITE, False, points)

def create_ray_one(black_hole, mx, my, location):
    dir_x = mx - location[0]
    dir_y = my - location[1]
    rays.append(Ray(location[0], location[1], black_hole, (dir_x, dir_y)))

def geodesic(ray, rhs, r_s_m):
    dphi = max(min(ray.dphi, 1e6), -1e6)
    dr = ray.dr

    r_px = max(ray.r, 1e-6)
    r_m = r_px * METERS_PER_PIXEL 

    term_m = (C_SI * C_SI * r_s_m) / (2.0 * r_m * r_m)

    term_px = term_m / METERS_PER_PIXEL 

    radial_acc_px = ray.r * (dphi ** 2) - term_px
    angular_acc = -2.0 * dr * dphi / max(ray.r, 1e-6)

    rhs.clear()
    rhs.extend([dr, dphi, radial_acc_px, angular_acc])


def add_state(a, b, factor, out):
    out.clear()
    out.extend([a[i] + factor * b[i] for i in range(4)])


def rk4_step(ray, black_hole, dlambda):
    if (ray.r < black_hole.r_px):
        return
    y0 = [ray.r, ray.phi, ray.dr, ray.dphi]
    k1, k2, k3, k4, temp = [], [], [], [], []

    geodesic(ray, k1, black_hole.r_si)
    add_state(y0, k1, dlambda / 2.0, temp)
    r2 = Ray(0, 0, black_hole, (0, 0))
    r2.r, r2.phi, r2.dr, r2.dphi = temp
    geodesic(r2, k2, black_hole.r_si)

    add_state(y0, k2, dlambda / 2.0, temp)
    r3 = Ray(0, 0, black_hole, (0, 0))
    r3.r, r3.phi, r3.dr, r3.dphi = temp
    geodesic(r3, k3, black_hole.r_si)

    add_state(y0, k3, dlambda, temp)
    r4 = Ray(0, 0, black_hole, (0, 0))
    r4.r, r4.phi, r4.dr, r4.dphi = temp
    geodesic(r4, k4, black_hole.r_si)

    ray.r += (dlambda / 6.0) * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0])
    ray.phi += (dlambda / 6.0) * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1])
    ray.dr += (dlambda / 6.0) * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2])
    ray.dphi += (dlambda / 6.0) * (k1[3] + 2.0 * k2[3] + 2.0 * k3[3] + k4[3])

def main():
    global state, sim_mode, rays, C_PX, METERS_PER_PIXEL, CURRENT_MASS_KG
    global CUSTOM_MASS_KG, CUSTOM_METERS_PER_PIXEL
    
    clock = pygame.time.Clock()
    running = True

    bl = None
    temp_ray_pos = None

    create_main_menu()

    while running:
        time_delta = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "simulation":
                        state = "main_menu"
                        rays.clear()
                        bl = None
                        temp_ray_pos = None
                        create_main_menu()
                    elif state == "settings":
                        CUSTOM_MASS_KG = settings_mass_slider.get_current_value() * SOLAR_MASS
                        CUSTOM_METERS_PER_PIXEL = settings_mpp_slider.get_current_value()
                        destroy_settings_menu()
                        create_main_menu()
                        state = "main_menu"

            if state == "simulation":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        if temp_ray_pos is not None:
                            mx, my = pygame.mouse.get_pos()
                            if bl and math.hypot(temp_ray_pos[0] - bl.x, temp_ray_pos[1] - bl.y) < bl.r_px:
                                temp_ray_pos = None
                                print("Cannot fire ray from inside event horizon")
                            else:
                                create_ray_one(bl, mx, my, temp_ray_pos)
                            temp_ray_pos = None
                        else:
                            temp_ray_pos = pygame.mouse.get_pos()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if state == "main_menu":
                    if event.ui_element == main_menu_elements[0]: 
                        sim_mode = "interstellar"
                        CURRENT_MASS_KG = INTERSTELLAR_MASS_KG
                        METERS_PER_PIXEL = INTERSTELLAR_METERS_PER_PIXEL
                        C_PX = C_SI / METERS_PER_PIXEL
                        
                        bl = BlackHole(WIDTH // 2, HEIGHT // 2, CURRENT_MASS_KG)
                        destroy_main_menu()
                        state = "simulation"
                        
                    elif event.ui_element == main_menu_elements[2]: 
                        sim_mode = "custom"
                        CURRENT_MASS_KG = CUSTOM_MASS_KG
                        METERS_PER_PIXEL = CUSTOM_METERS_PER_PIXEL
                        C_PX = C_SI / METERS_PER_PIXEL
                        
                        bl = BlackHole(WIDTH // 2, HEIGHT // 2, CURRENT_MASS_KG)
                        destroy_main_menu()
                        state = "simulation"
                        
                    elif event.ui_element == main_menu_elements[4]: 
                        destroy_main_menu()
                        create_settings_menu()
                        state = "settings"
                
                elif state == "settings":
                    if event.ui_element == settings_ui_elements[4]: 

                        CUSTOM_MASS_KG = settings_mass_slider.get_current_value() * SOLAR_MASS
                        CUSTOM_METERS_PER_PIXEL = settings_mpp_slider.get_current_value()
                        
                        destroy_settings_menu()
                        create_main_menu()
                        state = "main_menu"

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                 if state == "settings":
                    if event.ui_element == settings_mass_slider:
                        settings_mass_label.set_text(f'Custom Mass Mult: {event.value:.0f}')
                    elif event.ui_element == settings_mpp_slider:
                        settings_mpp_label.set_text(f'Custom Meters/Pixel: {event.value:.2e}')

            manager.process_events(event)

        manager.update(time_delta)

        if state == "main_menu":
            win.blit(BG, (0, 0)) 
        
        elif state == "settings":
            win.blit(BG, (0, 0)) 

        elif state == "simulation":
            if sim_mode == "interstellar":
                win.blit(BG_INTERSTELLAR, (0, 0))
            else:
                win.blit(BG, (0, 0))
            
            if bl:
                for ray in rays[:]:
                    rk4_step(ray, bl, 1e-3)
                    ray.move(bl, 0)
                    ray.draw()
                    
                    off_screen = ray.x > WIDTH or ray.x < 0 or ray.y < 0 or ray.y > HEIGHT
                    inside_bh = ray.r < bl.r_px
                    if off_screen or inside_bh:
                        try:
                            rays.remove(ray)
                        except ValueError:
                            pass 
            
            if temp_ray_pos is not None:
                pygame.draw.circle(win, RED, temp_ray_pos, 3)
                pygame.draw.line(win, BLUE, temp_ray_pos, pygame.mouse.get_pos(), 1)

            if sim_mode == "custom" and bl:
                bl.draw()

        manager.draw_ui(win)
        
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()