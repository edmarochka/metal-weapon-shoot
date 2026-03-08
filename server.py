import customtkinter as ctk
from pygame import *
from time import sleep, time as get_time
from random import *
import socket
import json
import os

# --- МЕНЮ СЕРВЕРА ---
class ServerLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Metal Weapon - Server")
        self.geometry("300x300")
        ctk.CTkLabel(self, text="СТВОРИТИ ГРУ", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.port_entry = ctk.CTkEntry(self, placeholder_text="Порт (5555)")
        self.port_entry.insert(0, "5555")
        self.port_entry.pack(pady=10)

        ctk.CTkButton(self, text="ЗАПУСТИТИ СЕРВЕР", command=self.start).pack(pady=20)

    def start(self):
        port = int(self.port_entry.get())
        self.destroy()
        run_server("0.0.0.0", port) # 0.0.0.0 дозволяє підключення ззовні

def run_server(ip, port):
    init()
    font.init()
    WIDTH, HEIGHT = 800, 600
    screen = display.set_mode((WIDTH, HEIGHT))
    display.set_caption("Metal Weapon - SERVER (P1)")
    game_clock = time.Clock()

    P_SIZE, BULLET_SPEED, PLAYER_SPEED, RELOAD_TIME = 60, 12, 7, 0.4
    main_font = font.SysFont("Arial", 64, bold=True)

    def get_texture(file_name, color, flip=False):
        path = os.path.join(os.path.dirname(__file__), file_name)
        if os.path.exists(path):
            img = image.load(path).convert_alpha()
            img = transform.scale(img, (P_SIZE, P_SIZE))
            if flip: img = transform.rotate(img, 180)
            return img
        surf = Surface((P_SIZE, P_SIZE), SRCALPHA)
        draw.rect(surf, color, (0, 0, P_SIZE, P_SIZE), border_radius=10)
        return surf

    tex_p1 = get_texture("ocelot.png", (60, 60, 255), flip=True)
    tex_p2 = get_texture("solidsnake.jpg", (255, 60, 60), flip=False)

    # Мережа
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.listen(1)
    print("Waiting for client...")
    conn, addr = sock.accept()

    # Генерація мапи тільки сервером
    walls_data = [[randint(0, WIDTH-100), randint(200, HEIGHT-250), randint(80, 150), 30] for _ in range(7)]
    conn.send(json.dumps(walls_data).encode())
    walls = [Rect(w[0], w[1], w[2], w[3]) for w in walls_data]

    class Player:
        def __init__(self, x, y, tex):
            self.rect = Rect(x, y, P_SIZE, P_SIZE)
            self.tex = tex
            self.bullets = []
            self.hp = 100
            self.last_shot = 0

    me = Player(WIDTH//2 - 30, 40, tex_p1)
    enemy = Player(WIDTH//2 - 30, HEIGHT - 100, tex_p2)
    conn.setblocking(False)

    run = True
    while run:
        for e in event.get():
            if e.type == QUIT: run = False
            if e.type == KEYDOWN and e.key == K_w:
                if get_time() - me.last_shot > RELOAD_TIME:
                    me.bullets.append([me.rect.centerx - 4, me.rect.centery])
                    me.last_shot = get_time()

        keys = key.get_pressed()
        if keys[K_a] and me.rect.left > 0: me.rect.x -= PLAYER_SPEED
        if keys[K_d] and me.rect.right < WIDTH: me.rect.x += PLAYER_SPEED

        for b in me.bullets[:]:
            b[1] += BULLET_SPEED
            if any(Rect(b[0], b[1], 8, 20).colliderect(w) for w in walls) or b[1] > HEIGHT:
                me.bullets.remove(b)

        for eb in enemy.bullets:
            if Rect(eb[0], eb[1], 8, 20).colliderect(me.rect):
                me.hp -= 1

        try:
            conn.send(json.dumps({"x": me.rect.x, "bullets": me.bullets, "hp": me.hp}).encode())
            raw = conn.recv(4096).decode()
            if raw:
                data = json.loads(raw.split("}{")[-1] if "}{" in raw else raw)
                enemy.rect.x, enemy.bullets, enemy.hp = data["x"], data["bullets"], data["hp"]
        except: pass

        screen.fill((20, 20, 20))
        for w in walls: draw.rect(screen, (80, 80, 80), w, border_radius=5)
        screen.blit(me.tex, me.rect)
        screen.blit(enemy.tex, enemy.rect)
        for b in me.bullets + enemy.bullets: draw.rect(screen, (255, 230, 0), (b[0], b[1], 8, 20), border_radius=4)
        
        draw.rect(screen, (0, 255, 100), (20, 20, max(0, me.hp), 10))
        draw.rect(screen, (0, 255, 100), (WIDTH-120, 20, max(0, enemy.hp), 10))

        if me.hp <= 0 or enemy.hp <= 0:
            res = "GAME WON" if enemy.hp <= 0 else "GAME LOST"
            txt = main_font.render(res, True, (255,255,255))
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//2)))
            display.flip()
            sleep(3)
            run = False

        display.flip()
        game_clock.tick(60)
    conn.close()
    quit()

if __name__ == "__main__":
    ServerLauncher().mainloop()