import pygame
from pygame.locals import *
from pathlib import Path

pygame.init()
clock = pygame.time.Clock()
FPS = 60

# Definindo as dimensões da tela
largura = 800
altura = 600

# Crie a tela
tela = pygame.display.set_mode((largura, altura))

# Defina a cor do retângulo (R, G, B)
cor_ret = (10, 10, 250, 4)  # Vermelho

# Defina as coordenadas e dimensões do retângulo (x, y, largura, altura)
x_ret = 100
y_ret = 100
lar_ret = 200
alt_ret = 100

myRect = Rect(10, 10, 50, 50)

# Defina o título da janela
pygame.display.set_caption("Minha Tela Pygame")

# Classe de elementos da barra de texto
class TextBox:
    def __init__(self, x_pos, y_pos, width, height, rgba, text):

        # Posições e dimensões
        self.rect = Rect(x_pos, y_pos, width, height)
        self.rgba = rgba

        # Texto
        self.text = text
        self.text_position = (0,0)
        self.font = pygame.font.Font(None, 36)
        self.font_color = (0, 0, 0)

        # Superfície própria da caixa de texto
        self.surface = pygame.Surface(pygame.Rect(self.rect).size, pygame.SRCALPHA)

        # largura das bordas, valor padrão: 10 (top, left, bottom, right)
        self.borders = [50, 20, 10, 10]

    def set_text(self, text):
        self.text = text

    def set_font_size(self, size):
        self.font.size = size

    def set_font(self, font):
        try:
            self.font = pygame.font.Font(font, self.font.size)
        except e:
            self.font = pygame.font.Font(None, self.font.size)

    def set_font_color(self, color):
        self.font_color = color
    
    def set_text_position(self, pos):
        self.text_position = pos

    def render_text(self, surface):
        shift = [self.borders[0] + self.text_position[0], self.borders[1] + self.text_position[1]]

        line_height = self.font.get_linesize()

        # Divide o texto em linhas
        lines = self.text.split('\n')

        # Renderiza o texto em uma superfície
        

        # Renderiza cada linha do texto
        for line in lines:
            text_to_render = self.font.render(line, True, self.font_color)
            self.surface.blit(text_to_render, tuple(shift))
            shift[1] += line_height 

        surface.blit(self.surface, self.rect)

    def draw_rect_alpha(self, surface):
        # Separando as componenetes do código de cor
        rgb = self.rgba[:3]
        alpha = self.rgba[3]

        # Desenhando o retângulo
        self.surface.set_alpha(alpha)
        pygame.draw.rect(self.surface, rgb, self.surface.get_rect())
        surface.blit(self.surface, self.rect)

tela.fill((255, 255, 255))

string = "\n"
box = TextBox(0, altura*(1/3), 
              largura, altura/3, 
              (29, 39, 60, 50), 
              f"(Ohhh yeah, right here! \nSherlock Holmes II, baby!)")

underBox = TextBox(largura/2, altura/2,
                   largura/4, altura/4,
                   (100, 100, 23, 240),
                   "")

RUNNING = True
# Loop de gerenciamento de eventos
try:
    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False

        underBox.draw_rect_alpha(tela)
        box.draw_rect_alpha(tela)
        box.set_font_color((121,172,220))
        box.render_text(tela)

        pygame.display.update()
        clock.tick(60)
        
except KeyboardInterrupt:
    pass
except Exception as e:
    print(str(e))

# Encerra o pygame
pygame.quit()