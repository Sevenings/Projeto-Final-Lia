import pygame
from pygame.locals import *
from pathlib import Path
import json
import threading
from time import sleep
from random import randint
import speech_recognition as sr


pygame.init()
clock = pygame.time.Clock()
FPS = 60

LANG = 'en'


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

    def addObject(self, *objs):
        for o in objs:
            self.cena.append(o)
            o.setScreen(self)
        return

    def update(self, time):
        for obj in self.cena:
            obj.update(time)
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

    def getBackground(self):
        return self.background

    def screenSetup(self):
        for obj in self.cena:
            obj.screenSetup()


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
        self.loadImagesSetup(image_name)
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.screen = None

    def loadImagesSetup(self, image_name):
        images_path = 'assets'
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


class Background(GameObject):
    def __init__(self):
        super().__init__('background.png', (0, 0))
        #self.image = pygame.transform.scale(self.image, screen.size)

    def draw(self):
        self.screen.blit(self.image, self.getPos())


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




class Barraca(GameObject):
    def __init__(self):
        super().__init__('shop.png', (0, 0))
        self.rect.midbottom = venda_pos
        self.pos = self.rect.topleft
        self.produtos = loadItens('itens/itens.json')

    def draw(self): #Look Here
        size = self.image.get_size()
        self.screen.blit(self.image, self.getPos())







class Vendedor(GameObject):
    def __init__(self, assets_path):
        super().__init__(assets_path, (0, 0))
        self.scene_ratio = 0.69
        self.expr_name = None
        self.expression = None
        self.assets_path = assets_path

    # Override
    def loadImagesSetup(self, assets_path):
        self.image = pygame.image.load(f'{assets_path}/body.png')

    # Override
    def screenSetup(self):
        background = self.screen.getBackground()
        self.resizeImage(self.scene_ratio, background)  # resize Body

        self.expressionsDict = self.loadExpressions('assets/luks/expressions/')
        self.selectExpression('closedmouth')

        size = self.image.get_size()    # positionate
        k = 0.15 * self.image.get_height()
        self.setPos(background.center()[0]-size[0]/2, venda_pos[1] - k - size[1])

    def selectExpression(self, expression_name):
        self.expression = self.expressionsDict[expression_name]
        self.expr_name = expression_name

    def setIdleExpression(self):
        self.selectExpression('closedmouth')

    def loadExpressions(self, directory_path):
        background = self.screen.getBackground()
        images = dict()
        with Path(directory_path) as directory :
            paths = [x for x in directory.iterdir() if not x.is_dir()]
            for image_path in paths:
                temp_image = pygame.image.load(image_path)
                temp_image = self.resizeThisImage(temp_image, self.scene_ratio, background)
                images[image_path.stem] = temp_image
                print(image_path.stem)
        return images

    def getExpressionName(self):
        return self.expr_name

    def getExpression(self):
        return self.expression

    def piscar(self):
        anterior = self.getExpressionName()
        self.selectExpression('blink')
        sleep(0.2)
        self.selectExpression(anterior)

    # Override
    def draw(self):
        pos = self.getPos()
        self.screen.blit(self.image, pos)
        self.screen.blit(self.expression, pos)

    # Override
    def update(self, time):
        #print(time)
        if time%40 == 0:
            threading.Thread(target=self.piscar).start()
            



class Script:
    def __init__(self):
        self.usos = 0
        self.roteiro = None
        self.limite = 0
        self.setup()
    
    def setup(self):
        pass

    def update(self, time, *args):
        self.action(time, args)
        self.usos += 1
        if self.usos == self.limite:
            return self.finish()

    def action(self, time, *args):
        pass

    def finish(self):
        self.roteiro.next()


class Roteiro:
    def __init__(self):
        self.roteiro = []
        self.selected = 0
        self.time = 0
        self.playing = False
        self.looping = False
        self.has_skipped = False

    def addScript(self, *scripts):
        for script in scripts:
            self.roteiro.append(script)
            script.roteiro = self

    def getSelectedScript(self):
        return self.roteiro[self.selected]

    def play(self):
        self.selected = 0
        self.playing = True

    def stop(self):
        self.playing = False

    def next(self):
        self.time = 0
        self.selected += 1
        maximum = len(self.roteiro)
        if self.selected >= maximum:
            if self.looping:
                self.selected = 0
            else:
                self.stop()
        self.has_skipped = True

    def update(self):
        if not self.playing:
            return
        script = self.getSelectedScript()
        script.update(self.time)
        if self.has_skipped:
            self.has_skipped = False
            return
        self.time += 1

# Script
class BoasVindas(Script):
    def setup(self):
        self.limite = 1

    def action(self, time, *args):
        print("Seja bem vindo à nossa Loja!")
        print("Temos dos mais diversos produtos!")


# Script
class Atendimento(Script):
    def __init__(self, vendedor):
        super().__init__()
        self.vendedor = vendedor

    def action(self, time, *args):
        if time > 0:
            return
        threading.Thread(target=self.atendimento, args=(self.vendedor,)).start()

    def atendimento(self, vendedor):
        global RUNNING, LANG
        r = sr.Recognizer()
        with sr.Microphone() as source:
            while RUNNING:
                audio = r.listen(source)
                try:
                    vendedor.selectExpression('thinker')

                    comando = r.recognize_google(audio, language=LANG)
                    print(comando)

                    vendedor.setIdleExpression()
                except sr.exceptions.UnknownValueError:
                    print("Não reconheci")
            self.finish()


# Script
class Zoom(Script):
    def __init__(self, camera, initialZoom, finalZoom, duration):
        super().__init__()
        self.initialZoom = initialZoom
        self.camera = camera
        self.finalZoom = finalZoom
        self.duration = duration

    def action(self, time, *args):
        if time > 0:
            return
        threading.Thread(target=self.makeZoom).start()

    def makeZoom(self):
        zi = self.initialZoom
        zo = self.finalZoom
        duration = self.duration

        for i in range(duration):
            self.camera.zoom = i/duration * (zo - zi) + zi
            sleep(0.5/duration)

        self.finish()

        



'''
class Animation:
    def __init__(self, *frames):
        self.frames = []
        self.actual_frame = 0
        self.playing = False
        self.looping = False

    def play(self):
        self.playing = True
        self.actual_frame = 0

    def addFrames(self, *images):
        for image in images:
            self.frames.append(image)

    def stop(self):
        self.playing = False

    def getFrame(self):
        return self.frames[self.actual_frame]

    def next(self):
        self.actual_frame += 1
        if self.actual_frame >= len(self.frames):
            if self.looping:
                self.actual_frame = 0
            else:
                self.stop()

    def update(self):
        self.next()
'''






# Criando objetos da Cena
venda_pos = (background.center()[0], background.size()[1]*0.98)
barraca = Barraca()
vendedor = Vendedor('assets/luks')

screen.addObject(background, vendedor, barraca)

screen.setBackground(background)
screen.screenSetup()

roteiro = Roteiro()
roteiro.addScript(Zoom(camera, 1, 1.5, 100), BoasVindas(), Atendimento(vendedor))
roteiro.play()


print("--------------------")
print("PRODUTOS CARREGADOS!")
for produto in barraca.produtos:
    print(produto.name, produto.type, produto.price, produto.image)
print("--------------------")




RUNNING = True
TIME = 0
while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False
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

    roteiro.update()

    screen.display.fill('black')

    screen.update(TIME)

    pygame.display.flip()

    clock.tick(FPS)  # limits FPS to 60
    TIME += 1

    #print(clock.get_fps())
pygame.quit()
