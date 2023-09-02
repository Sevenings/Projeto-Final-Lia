import pygame
from pygame.locals import *
from pathlib import Path
import json
import threading
from time import sleep
from random import randint
import speech_recognition as sr
from fastai.text.all import *
import os, re
import wave
import pyaudio


# Carrega o Classificador 
CLASSIFIER = load_learner("Modelo_NLP_Lia/colab_complete_model_vs1_0.pth")

pygame.init()
clock = pygame.time.Clock()
FPS = 60

#FONT = pygame.font.Font(size=24)

LANG = 'en'

MONEY = 100
INVENTORY = []

def listar(*args):
    print("Here! There are all my products:")
    print("Name \t Type \t Price")
    for produto in barraca.produtos:
        print(f"{produto.name} \t {produto.type} \t {produto.price}")


def comprar(*args): # (vendedor, produto)
    vendedor = args[0]
    threading.Thread(target=vendedor.getPaidExpression).start()
    produto = args[1][0]
    if produto is None:
        print("Sorry, don't undertand.")
        return
    global MONEY
    if produto.price > MONEY:
        print("Hey! You don't have enought money!")
        sleep(1)
        print(f"You only have {MONEY} coins.")
        return
    MONEY -= produto.price
    INVENTORY.append(produto)
    print(f"Alright! The {produto.name} is all yours!")
    return


def devolver(*args):
    threading.Thread(target=vendedor.refundExpression).start()
    print("You were refunded!")


def bom_dia(*args):
    print("Hello! Be welcome to my store!")
    sleep(1)
    print("How can I help you?")

def tchau(*args):
    global RUNNING
    RUNNING = False

CAT_LISTAGEM = 'LIST'
CAT_BUYING = 'BUY'
CAT_REFUNDING = 'REFUND'
CAT_HELLO = 'GREETING'
CAT_GOODBYE = 'GOODBYE'

ACTIONS = {
        CAT_LISTAGEM: listar,
        CAT_BUYING: comprar,
        CAT_REFUNDING: devolver,
        CAT_HELLO: bom_dia,
        CAT_GOODBYE: tchau
}


def findProduct(text):
    text = re.sub('[,.:;\'"!?-_+=]', '', text.lower())
    for product in barraca.produtos:
        if text.count(f' {product.name} '.lower()) > 0:
            return product
    return None


# Configurações do pyAudio
FORMAT = pyaudio.paInt16  # Formato de áudio (16 bits)
CHANNELS = 1  # Número de canais (mono)
RATE = 44100  # Taxa de amostragem em Hz
CHUNK = 1024  # Tamanho do buffer

# Inicializar PyAudio
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
stream.start_stream()

def salvar_audio(frames, path):

    try:
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            print(f"Áudio gravado salvo em {path}")
    except Exception as e:
        print(str(e))

class Screen:
    def __init__(self):
        self.size = (960*5/4, 520*5/4)
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
        camera.size = self.size

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
        self.pos = (x, y)

    def setCenter(self, x, y):
        self.setPos(x - self.size[0]/2, y - self.size[1]/2)

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
        self.screen.blit(self.image, self.getPos())

    def getProdutos(self):
        return self.produtos



def buyingRequestAbout(request, productList):
    for product in productList:
        name = product.name
        if request.find(name):
            return product
    return None







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

    def getPaidExpression(self):
        self.selectExpression('moneyeyes')
        sleep(2)
        self.setIdleExpression()

    def refundExpression(self):
        self.selectExpression('fearsad')
        sleep(1.5)
        self.setIdleExpression()

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


# Excessão de Interrupção de loop
class LoopInterrupt(Exception):
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(self.mensagem)

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
        global RUNNING, LANG, AUDIO_PRESSING
        #os.system('clear')

        # Caminho para o arquivo
        directory = os.path.dirname(os.path.abspath(__file__))
        subDir = "tmp"
        arquivo = "audio.wav"

        file_path = os.path.join(os.path.join(directory, subDir), arquivo)

        sleep(1/60)

        while RUNNING:

            try:
                frames = []  # Armazenar os quadros de áudio
                if AUDIO_PRESSING:
                    while True:
                        data = stream.read(CHUNK)
                        frames.append(data)
                        if not AUDIO_PRESSING: raise LoopInterrupt("Loop Interrompido")
            except LoopInterrupt:
                salvar_audio(frames, file_path)

                with sr.AudioFile(file_path) as source:
                    # Transcreve o audio para Texto 
                    success, comando = transcribe(source, vendedor)

                arguments = []

                if not success:
                    continue

                # Utiliza o Modelo para classificar 
                categoria = CLASSIFIER.predict(comando)[0]

                produto = None
                if categoria == CAT_BUYING or categoria == CAT_REFUNDING:
                    produto = findProduct(comando)
                    if produto:
                        arguments.append(produto)


                # Order Text Assemble
                order_text = f"{categoria}"
                if produto:
                    order_text += f' {produto.name}'

                # Ask if order is correct
                print(f"The order is '{order_text}', is that correct? [yes/no]") # TODO  Trocar por IA ou outra coisa
                success, comando = transcribe(source, vendedor)

                if not success or comando.lower() == 'no':
                    continue

                ACTIONS[categoria](vendedor, arguments)
        print("Finished")
        self.finish()




def transcribe(source, vendedor):

    if vendedor.getExpressionName() == 'thinker':
        vendedor.setIdleExpression()

    r = sr.Recognizer()
    audio = r.record(source)

    vendedor.selectExpression('thinker')
    try:
        comando = r.recognize_google(audio, language=LANG)
        print(f"I've heard: \"{comando}\"")
        return True, comando
    except sr.exceptions.UnknownValueError:
        print("Sorry, I didn't understand")
        return False, None



# Script
class Zoom(Script):
    def __init__(self, camera, initialZoom, finalZoom, finalPos, duration):
        super().__init__()
        self.initialZoom = initialZoom
        self.camera = camera
        self.finalZoom = finalZoom
        self.duration = duration
        self.finalPos = finalPos

    def action(self, time, *args):
        if time > 0:
            return
        threading.Thread(target=self.makeZoom).start()

    def makeZoom(self):
        zi = self.initialZoom
        zf = self.finalZoom
        pi = self.camera.getPos()
        pf = self.finalPos
        duration = self.duration

        for i in range(duration):
            self.camera.zoom = i/duration * (zf - zi) + zi
            self.camera.setPos(i/duration*(pf[0] - pi[0]) + pi[0], i/duration*(pf[1] - pi[1]) + pi[1])
            sleep(0.5/duration)
            # print(self.camera.pos, self.camera.zoom)

        self.finish()

        






# Criando objetos da Cena
venda_pos = (background.center()[0], background.size()[1]*0.98)
barraca = Barraca()
vendedor = Vendedor('assets/luks')

screen.addObject(background, vendedor, barraca)

screen.setBackground(background)
screen.screenSetup()

roteiro = Roteiro()
roteiro.addScript(Zoom(camera, 1, 1.5, (15, 90), 50), BoasVindas(), Atendimento(vendedor))
roteiro.play()

# Testando findProduct
texto = 'I would like an fruit, a phone charger! Please!'
produto = findProduct(texto)
print(produto)

'''
print("--------------------")
print("PRODUTOS CARREGADOS!")
listar()
print("--------------------")
'''




AUDIO_PRESSING = False
RUNNING = True
TIME = 0
try:
    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    os.system('clear')
                if event.key == pygame.K_q:
                    AUDIO_PRESSING = True if not AUDIO_PRESSING else False
                    
                    if not AUDIO_PRESSING:
                        print("not", end=" ")
                    print("Listening!")

                '''
                if event.key == pygame.K_a:
                    pos = camera.getPos()
                    camera.setPos(pos[0]-10, pos[1])
                elif event.key == pygame.K_d:
                    pos = camera.getPos()
                    camera.setPos(pos[0]+10, pos[1])
                elif event.key == pygame.K_w:
                    pos = camera.getPos()
                    camera.setPos(pos[0], pos[1]-10)
                elif event.key == pygame.K_s:
                    pos = camera.getPos()
                    camera.setPos(pos[0]-10, pos[1]+10)
                print(camera.getPos())
                '''
            '''
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_v:
                    AUDIO_PRESSING = False
                    print("Stopped.")
            '''


        roteiro.update()

        screen.display.fill('black')

        screen.update(TIME)

        pygame.display.flip()

        clock.tick(FPS)  # limits FPS to 60
        TIME += 1

except KeyboardInterrupt:
    pass
except Exception as e:
    print(str(e))

pygame.quit()
