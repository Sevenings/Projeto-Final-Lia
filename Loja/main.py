import pygame
from pygame.locals import *


pygame.init()
clock = pygame.time.Clock()
running = True


class Screen:
    def __init__(self):
        self.size = (2*960, 2*520)
        self.display = pygame.display.set_mode(self.size, flags=pygame.SCALED)   
        self.cena = []
        self.camera = None

    def blit(self, image, pos):
        cameraPos = self.camera.getPos()
        camCenter = self.camera.center()
        zoom = self.camera.zoom
        blitPos = (camCenter[0] + zoom*(pos[0]-camCenter[0]), camCenter[1] + zoom*(pos[1]-camCenter[1]))
        image = pygame.transform.scale_by(image, zoom)
        self.display.blit(image, blitPos)

    def center(self):
        return (self.size[0]/2, self.size[1]/2)

    def width(self):
        return self.size[0]

    def heigth(self):
        return self.size[1]

    def appendCamera(self, camera):
        self.camera = camera

    def addObject(self, obj):
        self.cena.append(obj)
        obj.setScreen(self)

screen = Screen()


class Camera:
    def __init__(self):
        self.size = (2*960, 2*520)
        self.pos = (0, 0)
        self.zoom = 0.5

    def center(self):
        return (self.size[0]/2 + self.pos[0], self.size[1]/2 + self.pos[1])

    def width(self):
        return self.size[0]

    def heigth(self):
        return self.size[1]

    def getPos(self):
        return self.pos

camera = Camera()
screen.appendCamera(camera)




class GameObject(pygame.sprite.Sprite):
    def setScreen(self, screen):
        self.screen = screen


class Background(GameObject):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('cenario.png')
        self.image = pygame.transform.scale(self.image, screen.size)
        self.screen = None
        self.pos = (0, 0)

    def draw(self):
        self.screen.blit(self.image, self.getPos())

    def getPos(self):
        return self.pos

    def update(self):
        self.draw()


background = Background()


venda_pos = (screen.center()[0], screen.size[1]*0.98)
class Barraca(GameObject):
    def __init__(self):
        k = 0.55
        self.image = pygame.image.load('vendinha.png')
        R = screen.width()/self.image.get_width()
        self.image = pygame.transform.scale_by(self.image, k*R)
        self.rect = self.image.get_rect()

        self.rect.midbottom = venda_pos
        
        self.screen = None

    def draw(self): #Look Here
        size = self.image.get_size()
        self.screen.blit(self.image, self.getPos())

    def getPos(self):
        return self.rect.topleft

    def update(self):
        self.draw()

barraca = Barraca()



class Vendedor(GameObject):
    def __init__(self):
        self.image = pygame.image.load('lukasfull.png')
        k = 0.69*screen.heigth()/self.image.get_size()[1]
        self.image = pygame.transform.scale_by(self.image, k)
        size = self.image.get_size()
        k = 0.15 * self.image.get_height()
        self.pos = (screen.center()[0]-size[0]/2, venda_pos[1] - k - size[1])
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.screen = None

    def update(self):
        self.screen.blit(self.image, self.pos)
    

vendedor = Vendedor()


cena = [background, vendedor, barraca]
for obj in cena:
    screen.addObject(obj)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                camera.pos = (camera.pos[0] + 50, camera.pos[1])
            elif event.key == pygame.K_a:
                camera.pos = (camera.pos[0] - 50, camera.pos[1])
            elif event.key == pygame.K_w:
                camera.pos = (camera.pos[0], camera.pos[1] - 50)
            elif event.key == pygame.K_s:
                camera.pos = (camera.pos[0], camera.pos[1] + 50)
            elif event.key == pygame.K_z:
                camera.zoom += 0.1
            elif event.key == pygame.K_x:
                camera.zoom -= 0.1

    screen.display.fill('black')


    for obj in cena:
        obj.update()

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
