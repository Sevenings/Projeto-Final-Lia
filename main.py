import pygame
from pygame.locals import *
from pathlib import Path
import json


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
        self.preCanvas.blit(image, pos)

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
    def __init__(self, image_name, pos):
        images_path = 'assets'
        self.image = pygame.image.load(f'{images_path}/{image_name}')
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.screen = None

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


class Background(GameObject):
    def __init__(self):
        super().__init__('background.png', (0, 0))
        #self.image = pygame.transform.scale(self.image, screen.size)

    def draw(self):
        self.screen.blit(self.image, self.getPos())

    def update(self):
        pass


background = Background()


class Item:
    def __init__(self, name, type, price, image_path):
        self.name = name
        self.type = type
        self.price = price
        self.image = None
        if image_path is not None:
            self.image = pygame.image.load(image_path)


def loadItens(path):
    file = open(path)
    json_data = json.loads(file.read())
    item_list = []
    for itemdata in json_data['itens']:
        name = itemdata['name']
        type = itemdata['type']
        price = itemdata['price']
        image_path = itemdata['image']
        item_list.append(Item(name, type, price, image_path))
    return item_list




venda_pos = (background.center()[0], background.size()[1]*0.98)
class Barraca(GameObject):
    def __init__(self):
        super().__init__('shop.png', (0, 0))
        self.rect.midbottom = venda_pos
        self.pos = self.rect.topleft
        self.produtos = loadItens('itens/itens.json')

    def draw(self): #Look Here
        size = self.image.get_size()
        self.screen.blit(self.image, self.getPos())

    def update(self):
        pass

barraca = Barraca()
print("--------------------")
print("PRODUTOS CARREGADOS!")
for produto in barraca.produtos:
    print(produto.name, produto.type, produto.price, produto.image)
print("--------------------")



class Vendedor(GameObject):
    def __init__(self):
        super().__init__('lks_seller.png', (0, 0))
        self.image = self.resizeImage(self.image)

        size = self.image.get_size()
        k = 0.15 * self.image.get_height()
        self.setPos(background.center()[0]-size[0]/2, venda_pos[1] - k - size[1])
        
        self.expressionsDict = self.loadExpressions('assets/expressions/')
        self.expression = None
        self.selectExpression('thinker')

    def selectExpression(self, expression_name):
        self.expression = self.expressionsDict[expression_name]

    def resizeImage(self, image):
        k = 0.69    # Fator de ajuste
        Ko = background.heigth()/image.get_size()[1]    # Fator de proporção
        return pygame.transform.scale_by(image, k*Ko)

    def loadExpressions(self, directory_path):
        images = dict()
        with Path(directory_path) as directory :
            paths = [x for x in directory.iterdir() if not x.is_dir()]
            for image_path in paths:
                images[image_path.stem] = self.resizeImage(pygame.image.load(image_path))
                print(image_path)
        return images

    def draw(self):
        pos = self.getPos()
        self.screen.blit(self.image, pos)
        self.screen.blit(self.expression, pos)

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
        '''
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
        '''

    screen.display.fill('black')

    screen.update()

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
