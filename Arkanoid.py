import pygame
import sys
from pygame.locals import *

pygame.init()

#nastavenie obrazovky
sirka_obrazu = 600
vyska_obrazu = 600
displej = pygame.display.set_mode((sirka_obrazu, vyska_obrazu))
pygame.display.set_caption("Arkanoid")
ikona = pygame.image.load('obrazky/arkanoid_ikona.png') 
pygame.display.set_icon(ikona)
pozadie = pygame.image.load("obrazky/arkanoid_pozadie.png").convert()

#nastavenie času
frames = pygame.time.Clock()
fps = 60

#font pre text
font = pygame.font.Font('freesansbold.ttf', 50)
font_maly = pygame.font.Font('freesansbold.ttf', 45)

#farba textu
TEXT_COL = (0, 0, 0)

#načítanie zvukových efektov
vyhra = pygame.mixer.Sound("obrazky/vyhra_zvuk.mp3")
prehra = pygame.mixer.Sound("obrazky/prehra_zvuk.mp3")
body = pygame.mixer.Sound("obrazky/plus_skore.mp3")
strata_zivota = pygame.mixer.Sound("obrazky/strata_zivota.mp3")


#načítanie hudby
pygame.mixer.init()
pygame.mixer.music.load('obrazky/hudba_pozadie.mp3')

#podprogram na vykreslenie textu
def draw_text(text, font, color, x, y, font_size=20):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    displej.blit(text_surface, text_rect)

def show_main_menu():
    while True:
        #zobrazenie pozadia
        displej.blit(pozadie, (0, 0))
        arkanoid_img = pygame.image.load("obrazky/arkanoid_menu.png").convert_alpha()
        arkanoid_img = pygame.transform.scale(arkanoid_img, (500, 200))
        displej.blit(arkanoid_img, (50, 100))
        #kreslenie textu so zmenšeným písmom
        draw_text("Stlač SPACE pre štart", font, TEXT_COL, 300, 400, 10)
        #update obrazovky
        pygame.display.update()
        #kontrola eventov
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mixer.music.play(-1)  #prehratie hudby po stlačení SPACE
                    return

#spustenie hlavného menu
show_main_menu()

#class

class Plocha:
    def __init__(self):
        self.vyska = 20
        self.sirka = 100
        self.x = 250
        self.y = 550
        self.rychlost = 10
        self.obdlznik = pygame.Rect(self.x, self.y, self.sirka, self.vyska)
        self.smer = 0
        self.texture = pygame.image.load("obrazky/plocha.png")
        self.texture = pygame.transform.scale(self.texture, (self.sirka, self.vyska))

    def pohyb(self):
        self.smer = 0
        klavesa = pygame.key.get_pressed()
        if klavesa[pygame.K_a] and self.obdlznik.left > 0:
            self.obdlznik.x -= self.rychlost
            self.smer = -1
        if klavesa[pygame.K_d] and self.obdlznik.right < sirka_obrazu:
            self.obdlznik.x += self.rychlost
            self.smer = 1

    def kreslenie(self):
        displej.blit(self.texture, (self.obdlznik.x, self.obdlznik.y))

class Lopta:
    def __init__(self, x, y):
        self.polomer = 10
        self.x = x - self.polomer
        self.y = y
        self.obdlznik = pygame.Rect(self.x, self.y, self.polomer * 2, self.polomer * 2)
        self.rychlost_x = 4
        self.rychlost_y = -4
        self.koniec_hry = False
        self.pocitadlo = 0
        self.texture = pygame.image.load("obrazky/lopta.png")
        self.texture = pygame.transform.scale(self.texture, (self.polomer * 2, self.polomer * 2))

    def pohyb(self):
        #ošetrenie aby zostalo v hráčskom okne
        if self.obdlznik.left < 0 or self.obdlznik.right > sirka_obrazu:
            self.rychlost_x *= -1

        if self.obdlznik.top < 0:
            self.rychlost_y *= -1

        if self.obdlznik.bottom > vyska_obrazu:
            self.rychlost_y *= -1
            self.pocitadlo -= 1

        #odraz lopty od hracovej plochy
        if self.obdlznik.colliderect(hracova_plocha.obdlznik):
            self.rychlost_y *= -1
                        
        self.obdlznik.x += self.rychlost_x
        self.obdlznik.y += self.rychlost_y

        return self.koniec_hry

    def kreslenie(self):
        displej.blit(self.texture, (self.obdlznik.x, self.obdlznik.y))

class Policka:
    def __init__(self):
        self.policka_sirka = 82
        self.policka_vyska = 35
        self.policka_riadky = 5
        self.policka_stlpce = 6
        self.policka_medzera = 15
        self.policka = []
        self.zoradenie()
        self.texture = pygame.image.load("obrazky/policka.png")
        self.texture = pygame.transform.scale(self.texture, (self.policka_sirka, self.policka_vyska))

    def zoradenie(self):
        for riadok in range(self.policka_riadky):
            for stlpec in range(self.policka_stlpce):
                policko = pygame.Rect(stlpec * (self.policka_sirka + self.policka_medzera ) + self.policka_medzera,
                                      riadok * (self.policka_vyska + self.policka_medzera ) + self.policka_medzera + 50,
                                      self.policka_sirka, self.policka_vyska)
                self.policka.append(policko)

    def kreslenie(self):
        for policko in self.policka:
            displej.blit(self.texture, (policko.x, policko.y))

class Zivoty:
    def __init__(self):
        self.zivot = 3
        self.texture = pygame.image.load('obrazky/zivoty.png')  
        self.texture = pygame.transform.scale(self.texture, (60, 60))

    def znizovanie_zivota(self):
        if lopta.obdlznik.bottom > vyska_obrazu:
            self.zivot -= 1
            strata_zivota.play()
            lopta.__init__(300, 520)
            hracova_plocha.obdlznik.x = 250
            if self.zivot == 0:
                pygame.mixer.music.stop()  #zastavenie hudby po prehre
                return True
            else:
                return False
        return False

    def kreslenie(self):
        text = font.render(str(self.zivot), True, "black")
        text_rect = text.get_rect()
        text_rect.center = (105, 35)
        displej.blit(text, text_rect)
        
        texture_rect = self.texture.get_rect()
        texture_rect.center = (text_rect.left - 30, 32)
        displej.blit(self.texture, texture_rect)
        
class Skore:
    def __init__(self):
        self.skore = 0
        self.texture = pygame.image.load('obrazky/skore.png')  
        self.texture = pygame.transform.scale(self.texture, (90, 90))

#kolizia lopta - policka a zvysovanie skore
    def zvysovanie_skore(self):
        for policko in policka.policka[:]:
            if lopta.obdlznik.colliderect(policko):
                policka.policka.remove(policko)
                lopta.rychlost_y *= -1
                self.skore += 1
                body.play()
                if self.skore == 30:
                    pygame.mixer.music.stop()  #zastavenie hudby po výhre
                    return True
                else:
                    return False
        return False

    def kreslenie(self):
        text = font.render(str(self.skore), True, "black")
        text_rect = text.get_rect()
        text_rect.center = (535, 35)
        displej.blit(text, text_rect)
        
        texture_rect = self.texture.get_rect()
        texture_rect.center = (text_rect.left - 50, 32)
        displej.blit(self.texture, texture_rect)

#vytvorenie premennych
hracova_plocha = Plocha()
lopta = Lopta(300, hracova_plocha.y - hracova_plocha.vyska)
policka = Policka()
zivoty = Zivoty()
skore = Skore()

#loop
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()

    displej.blit(pozadie, (0, 0))
    hracova_plocha.pohyb()
    hracova_plocha.kreslenie()
    lopta.kreslenie()
    lopta.pohyb()
    policka.kreslenie()
    zivoty.kreslenie()
    
    if zivoty.znizovanie_zivota():
        prehra.play()
        displej.blit(pygame.image.load("obrazky/prehra.png").convert(), (0, 0))
        pygame.display.update()
        pygame.time.delay(3500)
        pygame.quit()
        sys.exit()
    
    skore.kreslenie()
    if skore.zvysovanie_skore():
        vyhra.play()
        displej.blit(pygame.image.load("obrazky/výhra.png").convert(), (0, 0))
        pygame.display.update()
        pygame.time.delay(4500)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    frames.tick(fps)
