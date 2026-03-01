import pygame
import random
import time
import os

# Ініціалізація
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vertical Duel with Textures")
clock = pygame.time.Clock()

# Кольори
BLACK = (20, 20, 20)
GRAY = (80, 80, 80)
YELLOW = (255, 230, 0)
GREEN = (0, 255, 100)
RED = (255, 50, 50)

# Налаштування
P_SIZE = 60 # Трохи збільшили для кращої видимості текстур
BULLET_SPEED = 12
PLAYER_SPEED = 7
RELOAD_TIME = 0.4

# --- Функція для завантаження текстур ---
def get_texture(file_name, color, flip=False):
    if os.path.exists(file_name):
        img = pygame.image.load(file_name).convert_alpha()
        img = pygame.transform.scale(img, (P_SIZE, P_SIZE))
        if flip:
            img = pygame.transform.rotate(img, 180) # Розгортаємо верхнього гравця
        return img
    else:
        # Якщо файлу немає, створюємо кольоровий квадрат
        surf = pygame.Surface((P_SIZE, P_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0, 0, P_SIZE, P_SIZE), border_radius=10)
        if flip: pygame.draw.rect(surf, (255,255,255), (10, 35, 40, 10)) # Помітка "носа"
        else: pygame.draw.rect(surf, (255,255,255), (10, 5, 40, 10))
        return surf

# Завантажуємо текстури
tex_p1 = get_texture("ocelot.png", (60, 60, 255), flip=True)   # Верхній
tex_p2 = get_texture("solidsnake.jpg", (255, 60, 60), flip=False) # Нижній

class Player:
    def __init__(self, x, y, texture, controls, bullet_dir):
        self.rect = pygame.Rect(x, y, P_SIZE, P_SIZE)
        self.texture = texture
        self.controls = controls # [ліво, право, вогонь]
        self.bullet_dir = bullet_dir
        self.bullets = []
        self.hp = 100
        self.last_shot = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[self.controls[0]] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[self.controls[1]] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED

    def shoot(self):
        current_time = time.time()
        if current_time - self.last_shot > RELOAD_TIME:
            # Куля вилітає з центру гравця
            b_rect = pygame.Rect(self.rect.centerx - 4, self.rect.centery, 8, 20)
            self.bullets.append(b_rect)
            self.last_shot = current_time

def generate_map():
    obs = []
    for _ in range(7):
        w, h = random.randint(80, 150), random.randint(20, 35)
        x = random.randint(0, WIDTH - w)
        y = random.randint(200, HEIGHT - 250)
        obs.append(pygame.Rect(x, y, w, h))
    return obs

walls = generate_map()
p1 = Player(WIDTH//2 - P_SIZE//2, 40, tex_p1, [pygame.K_a, pygame.K_d, pygame.K_LSHIFT], 1)
p2 = Player(WIDTH//2 - P_SIZE//2, HEIGHT - 100, tex_p2, [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RCTRL], -1)

def update_logic():
    for p, opp in [(p1, p2), (p2, p1)]:
        p.move()
        for b in p.bullets[:]:
            b.y += p.bullet_dir * BULLET_SPEED
            
            # Вихід за межі
            if b.bottom < 0 or b.top > HEIGHT:
                p.bullets.remove(b)
                continue
            
            # Стіни
            hit_wall = False
            for w in walls:
                if b.colliderect(w):
                    p.bullets.remove(b)
                    hit_wall = True; break
            if hit_wall: continue
            
            # Влучання
            if b.colliderect(opp.rect):
                opp.hp -= 10
                p.bullets.remove(b)

def draw():
    screen.fill(BLACK)
    
    # Малюємо перешкоди
    for w in walls:
        pygame.draw.rect(screen, GRAY, w, border_radius=5)
    
    # Малюємо гравців (Текстури)
    screen.blit(p1.texture, p1.rect)
    screen.blit(p2.texture, p2.rect)
    
    # Кулі
    for b in p1.bullets: pygame.draw.rect(screen, YELLOW, b, border_radius=4)
    for b in p2.bullets: pygame.draw.rect(screen, YELLOW, b, border_radius=4)
    
    # UI (HP Бари)
    # P1 (Зверху)
    pygame.draw.rect(screen, (50, 0, 0), (WIDTH-120, 20, 100, 15))
    pygame.draw.rect(screen, GREEN, (WIDTH-120, 20, p1.hp, 15))
    # P2 (Знизу)
    pygame.draw.rect(screen, (50, 0, 0), (20, HEIGHT-35, 100, 15))
    pygame.draw.rect(screen, GREEN, (20, HEIGHT-35, p2.hp, 15))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == p1.controls[2]: p1.shoot()
            if event.key == p2.controls[2]: p2.shoot()

    update_logic()
    draw()
    
    if p1.hp <= 0 or p2.hp <= 0:
        print("GAME OVER")
        time.sleep(1)
        running = False
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()