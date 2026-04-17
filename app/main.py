# Lenguaje de programación 
# Allan González V- 28.660.376
# Andrés Reyes V- 30.520.333
# Fernando Reyes V-30.159.566
# Mitchael Ruíz V- 31.416.127

import pygame
import json
import os
import sys
import math
import random

# --- COLORES ---
NEGRO_FONDO = (10, 10, 15)
BLANCO = (255, 255, 255)
VERDE_NEON = (0, 255, 150)
ROJO_VIVO = (255, 60, 60)
AMARILLO_ORO = (255, 215, 0)
CYAN_PORTAL = (0, 200, 255)
GRIS_METAL = (100, 100, 110)

PALETA_NIVELES = {
    1: ((20, 25, 40), (80, 120, 255)),   
    2: ((40, 15, 35), (255, 80, 160)),   
    3: ((30, 10, 50), (180, 100, 255))   
}

def guardar_puntuacion(nombre, puntos):
    archivo = "puntuaciones.json"
    datos = []
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            try: datos = json.load(f)
            except: datos = []
    datos.append({"nombre": nombre, "puntos": puntos})
    datos = sorted(datos, key=lambda x: x["puntos"], reverse=True)
    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)
    return datos[:5]

# =========================================================
# ENEMIGO
# =========================================================
class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, size, muros):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = pygame.Rect(x + 2, y + 2, size - 4, size - 4)
        self.muros = muros
        self.velocidad = 2 
        self.dibujar()

    def dibujar(self):
        self.image.fill((0,0,0,0))
        pygame.draw.rect(self.image, ROJO_VIVO, (0, 0, self.size, self.size), border_radius=6)
        pygame.draw.polygon(self.image, BLANCO, [(5, 10), (12, 15), (5, 18)])
        pygame.draw.polygon(self.image, BLANCO, [(self.size-5, 10), (self.size-12, 15), (self.size-5, 18)])

    def update(self):
        self.rect.x += self.velocidad
        if pygame.sprite.spritecollideany(self, self.muros):
            self.velocidad *= -1
            self.rect.x += self.velocidad

# =========================================================
# PERSONAJE
# =========================================================
class Personaje(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, int(size * 0.7), int(size * 0.7))
        self.pos_inicio = (x, y)
        self.velocidad = 5
        self.ultimo_teleport = 0
        self.actualizar_cara()

    def actualizar_cara(self):
        self.image.fill((0,0,0,0))
        pygame.draw.rect(self.image, VERDE_NEON, (0, 0, self.size, self.size), border_radius=8)
        pygame.draw.circle(self.image, (0,0,0), (int(self.size//3), int(self.size//3)), 3)
        pygame.draw.circle(self.image, (0,0,0), (int(self.size*0.6), int(self.size//3)), 3)
        pygame.draw.arc(self.image, (0,0,0), (self.size//4, self.size//2, self.size//2, self.size//3), 3.14, 0, 3)

    def mover(self, dx, dy, muros):
        self.rect.x += dx * self.velocidad
        for m in pygame.sprite.spritecollide(self, muros, False):
            if dx > 0: self.rect.right = m.rect.left
            if dx < 0: self.rect.left = m.rect.right
        self.rect.y += dy * self.velocidad
        for m in pygame.sprite.spritecollide(self, muros, False):
            if dy > 0: self.rect.bottom = m.rect.top
            if dy < 0: self.rect.top = m.rect.bottom

    def reset(self):
        self.rect.topleft = self.pos_inicio

# =========================================================
# ELEMENTOS
# =========================================================
class Elemento(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo, size, color=(255,255,255)):
        super().__init__()
        self.tipo, self.size, self.color = tipo, size, color
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.h_actual = 0

    def update(self):
        self.image.fill((0,0,0,0))
        t = pygame.time.get_ticks() * 0.003
        if self.tipo == "1":
            pygame.draw.rect(self.image, self.color, (0, 0, self.size, self.size), border_radius=2)
        elif self.tipo == "C":
            pygame.draw.circle(self.image, AMARILLO_ORO, (self.size//2, self.size//2), self.size//4)
        elif self.tipo == "T":
            self.h_actual = (math.sin(t + self.rect.x) + 1) / 2
            for i in range(3):
                p = [(i*(self.size//3), self.size), ((i+0.5)*(self.size//3), self.size - (self.h_actual*self.size)), ((i+1)*(self.size//3), self.size)]
                pygame.draw.polygon(self.image, GRIS_METAL, p)
        elif self.tipo == "M":
            brillo = int(abs(math.sin(t*3)) * 100) + 155
            pygame.draw.rect(self.image, (brillo, brillo, 0), (2, 2, self.size-4, self.size-4), border_radius=4)
        elif self.tipo == "P":
            pygame.draw.ellipse(self.image, CYAN_PORTAL, (2, 2, self.size-4, self.size-4), 3)

# =========================================================
# CLASE PRINCIPAL
# =========================================================
class Fabirinto:
    def __init__(self):
        pygame.init()
        os.system('cls' if os.name == 'nt' else 'clear')
        self.nombre = input("INGRESA TU NOMBRE: ").upper() or "ANÓNIMO"
        self.screen = pygame.display.set_mode((1100, 900))
        self.fuente_m = pygame.font.SysFont("Impact", 40)
        self.fuente_p = pygame.font.SysFont("Consolas", 20, bold=True)
        self.nivel_actual, self.vidas, self.puntos = 1, 3, 0
        self.flash_portal = 0
        self.shake_amount = 0
        self.cargar_nivel()

    def cargar_nivel(self):
        self.all_sprites = pygame.sprite.Group()
        self.muros, self.metas, self.trampas, self.premios, self.enemigos, self.portales = [pygame.sprite.Group() for _ in range(6)]
        
        mapas = {
            1: (30, ["111111111111111111111111111111111","100000100C0000T00000100C000000001","101110101111111111101011111111101","1010000010P0E0000010101000E0C0101","101011111011111110101010111110101","1C1010000010000010100010100010101","101010111110111010111110101010101","10100010C00000100000000010100C101","101111101111111111111111101111101","1C000000100000P000000000000000CM1","111111111111111111111111111111111"]),
            2: (28, ["1111111111111111111111111111111","1000C0000100E00010C000000000001","1011111010111110101111111111101","1P1000001000001010100C000T00101","1010111111111010101011111110101","10001000E0C00010001010000010101","1110101111111111101010111010101","1000100C00000000001000101010C01","1011111111101011111110101111101","1C000000000C10000E00001P0C000M1","1111111111111111111111111111111"]),
            3: (22, ["1111111111111111111111111","1000C000010000C00000000C1","1011111101011111111111101","1P00000000000T00000E00001","1010111111011111111111111","101000C00100000000T0C0001","1011111011111111111111101","101000000E001000000C00001","1010111111101011111111111","1010000000001000000000001","1111111110111011111111101","1000000C0010000100C000T01","1011111111101111011111101","1000001000001000001000C01","1011101011111011111011101","1010C0100010P000001010011","1010111110111111101011101","1010000000000E0C001000101","1010111111101111111110101","1C00000010000010000C000M1","1111111111111111111111111"])
        }

        size, mapa = mapas[self.nivel_actual]
        ox, oy = (1100 - len(mapa[0])*size)//2, 100
        fondo, pared = PALETA_NIVELES[self.nivel_actual]
        self.color_fondo = fondo

        for r, fila in enumerate(mapa):
            for c, char in enumerate(fila):
                x, y = c*size+ox, r*size+oy
                if char == "1":
                    o = Elemento(x, y, "1", size, pared); self.muros.add(o); self.all_sprites.add(o)
                elif char == "E":
                    en = Enemigo(x, y, size, self.muros); self.enemigos.add(en)
                elif char == "M":
                    o = Elemento(x, y, "M", size); self.metas.add(o); self.all_sprites.add(o)
                elif char == "T":
                    o = Elemento(x, y, "T", size); self.trampas.add(o); self.all_sprites.add(o)
                elif char == "C":
                    o = Elemento(x, y, "C", size); self.premios.add(o); self.all_sprites.add(o)
                elif char == "P":
                    o = Elemento(x, y, "P", size); self.portales.add(o); self.all_sprites.add(o)

        self.pj = Personaje(ox+size, oy+size, int(size*0.8))
        self.tiempo = 100

    def pantalla_stats(self, titulo, sub):
        esperando = True
        while esperando:
            overlay = pygame.Surface((1100, 900))
            overlay.set_alpha(180)
            overlay.fill((20, 20, 30))
            self.screen.blit(overlay, (0,0))
            
            pygame.draw.rect(self.screen, CYAN_PORTAL, (300, 250, 500, 400), 2, border_radius=15)
            
            t_surf = self.fuente_m.render(titulo, True, VERDE_NEON)
            s_surf = self.fuente_p.render(sub, True, BLANCO)
            p_surf = self.fuente_m.render(f"PUNTAJE: {self.puntos}", True, AMARILLO_ORO)
            e_surf = self.fuente_p.render("Presiona [ENTER] para continuar", True, CYAN_PORTAL)
            
            self.screen.blit(t_surf, t_surf.get_rect(center=(550, 320)))
            self.screen.blit(s_surf, s_surf.get_rect(center=(550, 380)))
            self.screen.blit(p_surf, p_surf.get_rect(center=(550, 460)))
            self.screen.blit(e_surf, e_surf.get_rect(center=(550, 600)))
            
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN: esperando = False

    def morir(self):
        self.shake_amount = 20
        flash = pygame.Surface((1100, 900))
        flash.fill(ROJO_VIVO); flash.set_alpha(150)
        self.screen.blit(flash, (0,0))
        pygame.display.flip(); pygame.time.delay(150)
        
        self.vidas -= 1
        if self.vidas <= 0: 
            self.final("GAME OVER", ROJO_VIVO)
        self.pj.reset(); self.tiempo = 100

    def ejecutar(self):
        reloj = pygame.time.Clock()
        u_seg = pygame.time.get_ticks()
        while True:
            reloj.tick(60)
            ahora = pygame.time.get_ticks()
            
            render_offset = [random.randint(-self.shake_amount, self.shake_amount) for _ in range(2)] if self.shake_amount > 0 else [0,0]
            if self.shake_amount > 0: self.shake_amount -= 1

            self.screen.fill(self.color_fondo)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()

            k = pygame.key.get_pressed()
            dx = (k[pygame.K_d] or k[pygame.K_RIGHT]) - (k[pygame.K_a] or k[pygame.K_LEFT])
            dy = (k[pygame.K_s] or k[pygame.K_DOWN]) - (k[pygame.K_w] or k[pygame.K_UP])
            
            self.pj.mover(dx, dy, self.muros)
            self.all_sprites.update(); self.enemigos.update()

            hits_p = pygame.sprite.spritecollide(self.pj, self.portales, False)
            if hits_p and (ahora - self.pj.ultimo_teleport > 1000):
                for p in self.portales:
                    if p != hits_p[0]:
                        self.pj.rect.center = p.rect.center
                        self.pj.ultimo_teleport = ahora
                        self.flash_portal = 15; break

            if pygame.sprite.spritecollideany(self.pj, self.enemigos): self.morir()
            for t in self.trampas:
                if pygame.sprite.collide_rect(self.pj, t) and t.h_actual > 0.7: self.morir()
            
            if pygame.sprite.spritecollide(self.pj, self.premios, True): self.puntos += 50
            
            if pygame.sprite.spritecollideany(self.pj, self.metas):
                if self.nivel_actual < 3:
                    self.pantalla_stats(f"¡NIVEL {self.nivel_actual} COMPLETADO!", "Prepárate para el siguiente reto.")
                    self.nivel_actual += 1; self.cargar_nivel()
                else: self.final("VICTORIA TOTAL", VERDE_NEON)

            if ahora - u_seg >= 1000:
                self.tiempo -= 1; u_seg = ahora
                if self.tiempo <= 0: self.morir()

            game_surf = pygame.Surface((1100, 900), pygame.SRCALPHA)
            self.all_sprites.draw(game_surf); self.enemigos.draw(game_surf)
            game_surf.blit(self.pj.image, self.pj.rect)
            self.screen.blit(game_surf, render_offset)

            if self.flash_portal > 0:
                s = pygame.Surface((1100, 900)); s.set_alpha(self.flash_portal * 15); s.fill(CYAN_PORTAL)
                self.screen.blit(s, (0,0)); self.flash_portal -= 1

            pygame.draw.rect(self.screen, (10,10,20), (0,0,1100,70))
            info = f" {self.nombre} | LVL: {self.nivel_actual} | PTS: {self.puntos} | VIDAS: {self.vidas} | TIME: {self.tiempo}s"
            self.screen.blit(self.fuente_p.render(info, True, BLANCO), (20, 25))
            pygame.display.flip()

    def final(self, t, c):
        top_5 = guardar_puntuacion(self.nombre, self.puntos)
        
        esperando = True
        while esperando:
            self.screen.fill(NEGRO_FONDO)
            
            # Título
            texto_titulo = t if t != "VICTORIA TOTAL" else "¡VICTORIA TOTAL, LO LOGRASTE!"
            txt_v = self.fuente_m.render(texto_titulo, True, c)
            self.screen.blit(txt_v, txt_v.get_rect(center=(550, 150)))
            
            # Tabla de Records
            pygame.draw.rect(self.screen, GRIS_METAL, (350, 230, 400, 480), 2, border_radius=10)
            tit_rec = self.fuente_p.render("--- HALL OF FAME ---", True, AMARILLO_ORO)
            self.screen.blit(tit_rec, tit_rec.get_rect(center=(550, 270)))
            
            for i, jug in enumerate(top_5):
                color_record = VERDE_NEON if jug["nombre"] == self.nombre and jug["puntos"] == self.puntos else BLANCO
                linea = f"{i+1}. {jug['nombre']} ...... {jug['puntos']} pts"
                r_surf = self.fuente_p.render(linea, True, color_record)
                self.screen.blit(r_surf, (400, 320 + i*55))

            # Instrucción de salida
            exit_surf = self.fuente_p.render("Presiona [ENTER] para salir del juego", True, CYAN_PORTAL)
            self.screen.blit(exit_surf, exit_surf.get_rect(center=(550, 780)))

            pygame.display.flip()
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN: esperando = False

        pygame.quit(); sys.exit()

if __name__ == "__main__":
    Fabirinto().ejecutar()
