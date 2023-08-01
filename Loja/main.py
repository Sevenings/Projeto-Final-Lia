import pygame
from pygame.locals import *


pygame.init()
clock = pygame.time.Clock()


class Screen:
    def __init__(self):
        self.size = (960, 520)
        self.display = pygame.display.set_mode(self.size, flags=pygame.SCALED)   
        self.cena = []
        self.camera = None
        self.background = None
        self.preCanvas = None

    def blit(self, image, pos):
        camPos = self.camera.getPos()
        camWidth = self.camera.width()
        camHeigth = self.camera.heigth()
        blitPos = (pos[0], pos[1])
        self.preCanvas.blit(image, blitPos)

    def center(self):
        return (self.size[0]/2, self.size[1]/2)

    def width(self):
        return self.size[0]

    def heigth(self):
        return self.size[1]

    def appendCamera(self, camera):
        self.camera = camera
        camera.screen = self

    def addObject(self, obj):
        self.cena.append(obj)
        obj.setScreen(self)

    def update(self):
        for obj in self.cena:
            obj.update()
        self.draw()

    def draw(self):
        self.preCanvas.fill('black')
        for obj in self.cena:
            obj.draw()
        self.drawDisplay()

    def drawDisplay(self):
        camPos = self.camera.getPos()
        camCenter = self.camera.center()
        camSize = self.camera.size
        zoom = self.camera.zoom

        Ko = camSize[1]/self.background.heigth()
        image = pygame.transform.smoothscale_by(self.preCanvas, Ko*zoom)
        pos = (camCenter[0] - zoom*camSize[0]/2, camCenter[1] - zoom*camSize[1]/2)
        self.display.blit(image, pos)

    def setBackground(self, background):
        self.background = background
        self.preCanvas = pygame.Surface(self.background.size())

screen = Screen()


class Camera:
    def __init__(self):
        self.size = (960, 520)
        self.pos = (0, 0)
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
        self.pos = (x, y)

camera = Camera()
screen.appendCamera(camera)



class GameObject(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        self.image = pygame.image.load(image)
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.screen = None

    def setPos(self, x, y):
        self.pos = (x, y)
        self.rect.topleft = self.pos

    #def setPos(self, pos):
        #self.setPos(pos[0], pos[1])

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


class Background(GameObject):
    def __init__(self):
        super().__init__('cenario.png', (0, 0))
        #self.image = pygame.transform.scale(self.image, screen.size)

    def draw(self):
        self.screen.blit(self.image, self.getPos())

    def update(self):
        pass


background = Background()


venda_pos = (background.center()[0], background.size()[1]*0.98)
class Barraca(GameObject):
    def __init__(self):
        super().__init__('vendinha.png', (0, 0))
        self.rect.midbottom = venda_pos
        self.pos = self.rect.topleft
        #k = 0.55
        #R = screen.width()/self.image.get_width()
        #self.image = pygame.transform.scale_by(self.image, k*R)

    def draw(self): #Look Here
        size = self.image.get_size()
        self.screen.blit(self.image, self.getPos())

    def update(self):
        pass

barraca = Barraca()



class Vendedor(GameObject):
    def __init__(self):
        super().__init__('lukasfull.png', (0, 0))
        k = 0.69*background.heigth()/self.image.get_size()[1]
        self.image = pygame.transform.scale_by(self.image, k)
        size = self.image.get_size()
        k = 0.15 * self.image.get_height()
        self.setPos(background.center()[0]-size[0]/2, venda_pos[1] - k - size[1])

    def draw(self):
        self.screen.blit(self.image, self.pos)

    def update(self):
        pass

vendedor = Vendedor()


cena = [background, vendedor, barraca]
for obj in cena:
    screen.addObject(obj)

screen.setBackground(background)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                camera.pos = (camera.pos[0] + 10, camera.pos[1])
            elif event.key == pygame.K_a:
                camera.pos = (camera.pos[0] - 10, camera.pos[1])
            elif event.key == pygame.K_w:
                camera.pos = (camera.pos[0], camera.pos[1] - 10)
            elif event.key == pygame.K_s:
                camera.pos = (camera.pos[0], camera.pos[1] + 10)
            elif event.key == pygame.K_z:
                camera.zoom += 0.1
            elif event.key == pygame.K_x:
                camera.zoom -= 0.1

            print(camera.pos)

    screen.display.fill('black')

    screen.update()

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
