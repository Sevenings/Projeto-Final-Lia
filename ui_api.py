import pygame
from pygame.locals import *
from pathlib import Path

pygame.init()

PATH_ASSETS = 'assets'

# Classe da Janela do Jogo
class Screen:
    def __init__(self):
        self.size = (960*5/4, 520*5/4)
        self.display = pygame.display.set_mode(self.size, flags=pygame.SCALED)   
        self.cena = []
        self.ui = []
        self.camera = None
        self.background = None
        self.preCanvas = None

    def blit(self, image, pos):
        # Desenha uma imagem na tela
        self.preCanvas.blit(image, pos)

    def center(self):
        # Retorna o centro da Janela
        return (self.size[0]/2, self.size[1]/2)

    def width(self):
        # Retorna a largura da Janela
        return self.size[0]

    def heigth(self):
        # Retorna a altura da Janela
        return self.size[1]

    def appendCamera(self, camera):
        # Adiciona uma Câmera à Screen
        self.camera = camera
        camera.screen = self
        camera.size = self.size

    def addObject(self, *objs):
        # Vincula Objetos à Screen
        for o in objs:
            self.cena.append(o)
            o.setScreen(self)
        return

    def addUIObject(self, *objs):
        # Adiciona um elemento de UI à Screen
        for o in objs:
            self.ui.append(o)
            o.setScreen(self)
        return

    def update(self, time):
        # Update em todos os objetos
        for obj in self.cena:
            obj.update(time)
        for obj in self.ui:
            obj.update(time)
        self.draw()

    def draw(self):
        # Desenha todos os objetos da cena na Janela
        # Toda a pipeline está encapsulada aqui
        self.preCanvas.fill('black')
        for obj in self.cena:
            obj.draw()
        self.drawDisplay()
        self.drawUI()

    def drawDisplay(self):
        # Parte da Pipeline de draw
        # Pega o préCanvas, redimensiona e printa no display
        camPos = self.camera.getPos()
        camCenter = self.camera.center()
        camSize = self.camera.size
        zoom = self.camera.zoom

        Ko = camSize[1]/self.background.heigth()
        image = pygame.transform.smoothscale_by(self.preCanvas, Ko*zoom)
        pos = (camCenter[0] - zoom*camSize[0]/2, camCenter[1] - zoom*camSize[1]/2)
        self.display.blit(image, pos)

    def drawUI(self):
        for obj in self.ui:
            obj.draw(self.display)
            

    def setBackground(self, background):
        # Set Background
        self.background = background
        self.preCanvas = pygame.Surface(self.background.size())

    def getBackground(self):
        # Get Background
        return self.background

    def screenSetup(self):
        # Hook que a Screen envia para seus objetos
        for obj in self.cena:
            obj.screenSetup()

    def getDisplay(self):
        # Get Display
        return self.display


# Classe da Câmera do Jogo
class Camera:
    def __init__(self):
        self.size = None
        self.pos = (15, 0)
        self.zoom = 1
        self.screen = None

    def center(self):
        return (self.size[0]/2 + self.pos[0], self.size[1]/2 + self.pos[1])

    def width(self):
        return self.size[0]

    def heigth(self):
        return self.size[1]

    def getPos(self):
        return self.pos

    def setPos(self, x, y):
        # Positiona a Camera com TopLeft em x, y
        self.pos = (x, y)

    def setCenter(self, x, y):
        # Positiona a Camera com centro em x, y
        self.setPos(x - self.size[0]/2, y - self.size[1]/2)


# Classe Genérica para todos os objetos do Jogo
class GameObject(pygame.sprite.Sprite):
    def __init__(self, image_name, pos):
        self.loadImagesSetup(image_name)
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.screen = None

    def loadImagesSetup(self, image_name):
        images_path = PATH_ASSETS
        self.image = pygame.image.load(f'{images_path}/{image_name}')

    def setPos(self, x, y):
        self.pos = (x, y)
        self.rect.topleft = self.pos

    def getPos(self):
        return self.pos

    def setScreen(self, screen):
        self.screen = screen

    def size(self):
        return self.image.get_size()

    def getRect(self):
        return self.rect

    def center(self):
        return self.getRect().center

    def heigth(self):
        return self.image.get_height()

    def width(self):
        return self.image.get_width()

    def draw(self):
        pass

    def resizeImage(self, percent, ref_image):  
        k = percent
        Ko = ref_image.heigth()/self.image.get_size()[1]  # Baseado na Altura
        self.image = pygame.transform.scale_by(self.image, k*Ko)

    def resizeThisImage(self, input_image, percent, ref_image):
        k = percent
        Ko = ref_image.heigth()/input_image.get_size()[1]  # Baseado na Altura
        output = pygame.transform.scale_by(input_image, k*Ko)
        return output

    def screenSetup(self):
        pass

    def update(self, time):
        pass


# Classe do Background do Jogo
class Background(GameObject):
    def __init__(self, image_path):
        super().__init__(image_path, (0, 0))
        #self.image = pygame.transform.scale(self.image, screen.size)

    def draw(self):
        self.screen.blit(self.image, self.getPos())



# Classe de elementos da barra de texto
class TextBox:
    def __init__(self, x_pos, y_pos, width, height, rgba, text):
        # Screen
        self.screen = None

        # Posições e dimensões
        self.rect = Rect(x_pos, y_pos, width, height)
        self.rgba = rgba

        # Texto
        self.textBuffer = []
        self.text_position = (0,0)
        self.font = pygame.font.Font(None, 36)
        self.font_color = (0, 0, 0)

        # Superfície própria da caixa de texto
        self.surface = pygame.Surface(pygame.Rect(self.rect).size, pygame.SRCALPHA)

        # largura das bordas, valor padrão: 10 (top, left, bottom, right)
        self.borders = [50, 20, 10, 10]

    def addText(self, *textList):
        for text in textList:
            self.textBuffer.append(text)

    def getText(self):
        # Retorna o Texto Atual do Buffer de Texto
        if len(self.textBuffer) > 0:
            return self.textBuffer[0]
        else:
            return ''

    def setFontSize(self, size):
        self.font.size = size

    def setFont(self, font):
        try:
            self.font = pygame.font.Font(font, self.font.size)
        except e:
            self.font = pygame.font.Font(None, self.font.size)

    def setFontColor(self, color):
        self.font_color = color
    
    def setTextPosition(self, pos):
        self.text_position = pos

    def renderText(self, surface):
        shift = [self.borders[0] + self.text_position[0], self.borders[1] + self.text_position[1]]

        line_height = self.font.get_linesize()

        # Divide o texto em linhas
        lines = self.getText().split('\n')

        # Renderiza o texto em uma superfície
        

        # Renderiza cada linha do texto
        for line in lines:
            text_to_render = self.font.render(line, True, self.font_color)
            self.surface.blit(text_to_render, tuple(shift))
            shift[1] += line_height 

        surface.blit(self.surface, self.rect)

    def drawRectAlpha(self, surface):
        # Separando as componenetes do código de cor
        rgb = self.rgba[:3]
        alpha = self.rgba[3]

        # Desenhando o retângulo
        self.surface.set_alpha(alpha)
        pygame.draw.rect(self.surface, rgb, self.surface.get_rect())
        surface.blit(self.surface, self.rect)

    def draw(self, screen):
        self.drawRectAlpha(screen)
        self.renderText(screen)

    def setScreen(self, screen):
        self.screen = screen

    def screenSetup(self):
        pass

    def update(self, time):
        pass

    def interact(self):
        # Método para quando este elemento é interagido
        if len(self.textBuffer) > 0:
            self.textBuffer.pop(0)

        

