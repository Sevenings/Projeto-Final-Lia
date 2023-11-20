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
import pathlib
import platform
from ui_api import *

# Identifica o sistema operacional
sistema = platform.system()

# Adaptando script para sistema Windows
if sistema == "Windows":
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

# Caminho para o modelo
directory = os.path.dirname(os.path.abspath(__file__))
subDir = "Modelo_NLP_Lia"
arquivo = "colab_complete_model_vs1.0"

model_path = Path(os.path.join(os.path.join(directory, subDir), arquivo))

print(str(model_path))

# Carrega o Classificador 
CLASSIFIER = load_learner(model_path)

pygame.init()
clock = pygame.time.Clock()
FPS = 60


# Excessão de Interrupção de loop
class LoopInterrupt(Exception):
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(self.mensagem)


LANG = 'en'

MONEY = 100
INVENTORY = []


# Todas as ações que o feirante executa

def listar(*args):
    print("Here! There are all my products:")
    print("Name \t Type \t Price")
    for produto in barraca.produtos:
        print(f"{produto.name} \t {produto.type} \t {produto.price}")


def comprar(*args): # (vendedor, produto)
    vendedor = args[0]

    if len(args[1]) == 0:
        say("Didn't understand which product you'd like")
        return

    produto = args[1][0]

    global MONEY
    if produto.price > MONEY:
        say("Hey! You don't have enought money!", 
            f"You only have {MONEY} coins.")
        return
    MONEY -= produto.price
    INVENTORY.append(produto)

    threading.Thread(target=vendedor.getPaidExpression).start()
    say(f"Alright! The {produto.name} is all yours!",
         'Have a good day')
    return


def devolver(*args):
    threading.Thread(target=vendedor.refundExpression).start()
    say("You were refunded!", "I'm sorry")


def bom_dia(*args):
    say('Hello!', 'Be welcome to my store!','How can I help you?')

def tchau(*args):
    global RUNNING
    RUNNING = False

CAT_LISTAGEM = 'LIST'
CAT_BUYING = 'BUY'
CAT_REFUNDING = 'REFUND'
CAT_HELLO = 'GREETING'
CAT_GOODBYE = 'GOODBYE'

# Dicionário com as ações do feirante
ACTIONS = {
        CAT_LISTAGEM: listar,
        CAT_BUYING: comprar,
        CAT_REFUNDING: devolver,
        CAT_HELLO: bom_dia,
        CAT_GOODBYE: tchau
}


# Algorítmo que retorna o NOME identificando "De qual produto estamos falando?"
def classifyProductName(word, productList):
    word = word.lower()
    pontuacao_maior = 0
    for item in productList:
        referencia = item.name.lower()
        letras_comuns = 0
        tamanho = len(referencia)
        for i in range(tamanho):
            if word.startswith(referencia[:i+1]):
                letras_comuns += 1
            else:
                break
        if len(referencia) < len(word):
            tamanho = len(word)
        pontuacao = letras_comuns/tamanho # Calculo Pontuação
        # print(f'Word: {word}, Referencia: {referencia}, Item: {item.name}, Pontos: {pontuacao}')
        if pontuacao > pontuacao_maior:
            maior_item = item
            pontuacao_maior = pontuacao
    if pontuacao_maior >= 0.7: # Pontuação de Corte
        return maior_item
    return None

def findProduct(request, productList):
    possibilities = []
    for word in request.split():
        produto = classifyProductName(word, productList)
        if produto: 
            possibilities.append(produto)
    return possibilities



# Configurações do pyAudio
FORMAT = pyaudio.paInt16  # Formato de áudio (16 bits)
CHANNELS = 1  # Número de canais (mono)
RATE = 44100  # Taxa de amostragem em Hz
CHUNK = 1024  # Tamanho do buffer

# Inicializar PyAudio
p = pyaudio.PyAudio()

def createStream():
    return p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

# Salva frames de áudio em um arquivo de audio
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





# Classe Entrada de Áudio | 06-11-23 | 16:22
# Classe que mantem um Thread que captura o Audio
MESSAGE = None
HAS_NEW_MESSAGE = False
class EntradaAudio:
    def start(self):
        threading.Thread(target=self.audio_input, args=()).start()

    def audio_input(self):
        global RUNNING, AUDIO_PRESSING, MESSAGE, HAS_NEW_MESSAGE
        frames = list() # Armazenar os quadros de áudio
        while RUNNING:
            try:
                frames.clear()
                if AUDIO_PRESSING:
                    stream = createStream()
                    stream.start_stream()
                    while True:
                        data = stream.read(CHUNK)
                        frames.append(data)
                        # Se estiver ocorrendo uma captura de áudio e esta for interrompida, 
                        # a excessão LoopInterrupt é lançada e o programa passa para a parte 
                        # de processamento e gerenciamento do áudio
                        if not AUDIO_PRESSING:
                            stream.stop_stream()
                            stream.close()
                            raise LoopInterrupt("Loop Interrompido")
            except LoopInterrupt:
                # Salva os frames em um arquivo de áudio
                salvar_audio(frames, file_path)

                # Transcreve o áudio para Texto
                with sr.AudioFile(file_path) as source: 
                    success, comando = transcribe(source, vendedor)

                # Se a transcrição não for realizada com sucesso uma nova tentativa é
                # realizada
                if not success:
                    continue

                MESSAGE = comando
                HAS_NEW_MESSAGE = True

    def hasMessage(self):
        global HAS_NEW_MESSAGE
        return HAS_NEW_MESSAGE

    def readMessage(self):
        global HAS_NEW_MESSAGE, MESSAGE
        HAS_NEW_MESSAGE = False
        return MESSAGE

ENTRADA_AUDIO = EntradaAudio()
            







# Classe dos Itens
class Item:
    def __init__(self, name, type, price, image_path):
        self.name = name
        self.type = type
        self.price = price
        self.image = None
        if image_path is not None:
            self.image = pygame.image.load(image_path)


# Função para carregar todos os itens de um arquivo
# em uma lista de itens
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



# Criado Screen
screen = Screen()

# Criado Câmera
camera = Camera()
screen.appendCamera(camera)

# Criado Background
background = Background('background.png')

# Classe da Barraca do Jogo
class Barraca(GameObject):
    def __init__(self, image, pos):
        # Carrega os itens e os salva numa variável interna
        super().__init__(image, (0, 0))
        # Set pos
        self.rect.midbottom = pos
        self.pos = self.rect.topleft
        # Carrega Produtos
        self.produtos = loadItens('itens/itens.json')

    def draw(self): #Look Here
        self.screen.blit(self.image, self.getPos())

    def getProdutos(self):  # Função para acessar os itens
        return self.produtos






# Classe do Vendedor do Jogo
class Vendedor(GameObject):
    def __init__(self, assets_path):
        super().__init__(assets_path, (0, 0))
        # Tamanho em relação à cena
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

    def say(self, *text):
        texto = []
        for t in text:
            if type(t).__name__ == 'list' or type(t).__name__ == 'tuple':
                texto.extend(t)
            else:
                texto.append(t)

        screen = self.getScreen()
        textbox = TextBox(10, screen.heigth()-100-10, screen.width()-20, 100, (0, 0, 255, 255))
        textbox.setFontColor((255, 255, 255))
        for t in texto:
            textbox.addText(t)
        screen.addUIObject(textbox)

            



# Classe Script, que guarda cada "Cena" do jogo. 
# ex: Cena de dar zoom, cena de boas vindas, atendimento...
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

    def setLimite(self, l):
        self.limite = l

    def getLimite(self):
        return self.limite

    def finish(self):
        self.roteiro.next()



# Classe que guarda uma lista de Scripts
# e os "toca" numa ordem lógica
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
class AguardandoInteracao(Script):
    def action(self, time, *args):
        if not ENTRADA_AUDIO.hasMessage():
            return
        fala = ENTRADA_AUDIO.readMessage()

        categoria = CLASSIFIER.predict(fala)[0]

        if categoria == CAT_HELLO or categoria == CAT_LISTAGEM:
            self.finish()


        


# Script 
class BoasVindas(Script):
    def setup(self):
        self.setLimite(1)

    def action(self, time, *args):
        say("Hello! Be Welcome to my store!", "I have a huge variety of products!")



# Caminho para o arquivo de audio temporário
directory = os.path.dirname(os.path.abspath(__file__))
subDir = "tmp"
arquivo = "audio.wav"

file_path = os.path.join(os.path.join(directory, subDir), arquivo)

# Script de atendimento
class Atendimento(Script):
    def __init__(self, vendedor):
        super().__init__()
        self.vendedor = vendedor
        # A variável interaction indica o modo de interação
        # True -> O cliente tomou a iniciativa de interação
        # False -> O cliente está respondendo a uma pergunta
        self.interaction = True
        self.arguments = []
        self.categoria = None

    def action(self, time, *args):
        self.atendimento(self.vendedor)

    def atendimento(self, vendedor):  # Feito para ser executado em Thread
        if not ENTRADA_AUDIO.hasMessage():
            return
        comando = ENTRADA_AUDIO.readMessage()

        if self.interaction:
            self.arguments.clear()
            # Utiliza o Modelo para classificar 
            self.categoria = CLASSIFIER.predict(comando)[0]

            # Para as categorias de BUYING e REFUNDING
            # Que necessitam de um Produto como Argumento 
            # Identifica o produto pedido e o coloca na lista de argumentos
            produto = None
            if self.categoria == CAT_BUYING or self.categoria == CAT_REFUNDING:
                possiveisProdutos = findProduct(comando, barraca.getProdutos())
                print("Produtos encontrados")
                for p in possiveisProdutos:
                    if p: print(p.name)
                if len(possiveisProdutos) == 1:
                    produto = possiveisProdutos[0]
                elif len(possiveisProdutos) > 1:
                    print("Devo perguntar qual das opções é a correta")
                    # TODO Pergunte quais dos dois é o correto
                else:
                    print("Devo perguntar qual produto você quer")
                    # TODO Qual produto o player deseja
                
                if produto:
                    self.arguments.append(produto)
                print(self.arguments)


            # Cria uma string com a categoria e o produto
            order_text = f"{self.categoria}"
            if produto:
                order_text += f' {produto.name}'

            # Pergunta se a interação indentificada está correta
            say(f"The order is '{order_text}', is that correct? [yes/no]") # TODO  Trocar por IA ou outra coisa

            # A próxima etapa da interação vem do vendedor
            self.interaction = False
        else:

            # Se o programa tiver identificado a interação incorretamente,
            # nenhuma ação é tomada
            if comando.strip().lower() == 'no':
                return
            
            # A próxima etapa da interação vem do usuário
            self.interaction = True

            # Se o programa tiver identificado a interação corretamente,
            # a função correspondente é acionada
            ACTIONS[self.categoria](vendedor, self.arguments)

        # Tick
        sleep(1/60)
        print("Pre Finished")
        if not RUNNING:
            self.finish()
            print("Pos Finished")




# Recebe uma AUDIO_SOURCE e retorna o TEXTO transcrito
# Utilizada no Script Atendimento
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
    except Exception as e:
        print(str(e))
    finally:
        vendedor.setIdleExpression()



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



def say(*text):
    meu_vendedor = vendedor
    meu_vendedor.say(text)

def interact_text():
    for ui in screen.ui:
        ui.interact()






# Criando objetos da Cena
venda_pos = (background.center()[0], background.size()[1]*0.98)
barraca = Barraca('shop.png', venda_pos)
vendedor = Vendedor('assets/luks')

screen.addObject(background, vendedor, barraca) 

screen.setBackground(background)
screen.screenSetup()

roteiro = Roteiro()
roteiro.addScript(AguardandoInteracao(), Zoom(camera, 1, 1.5, (15, 90), 50), BoasVindas(), Atendimento(vendedor))
# roteiro.addScript(Zoom(camera, 1, 1.5, (15, 90), 50), BoasVindas(), Atendimento(vendedor))
roteiro.play()

# Testando findProduct
texto = 'I would like an fruit, two bananas! Please!'
resultado = findProduct(texto, barraca.produtos)
for x in resultado: print("Resultado da busca:", x.name)

# Testando classifyProductName
# resultado = classifyProductName('banana', barraca.getProdutos())
# print('Resultado da Classificação:', resultado.name)


'''
print("--------------------")
print("PRODUTOS CARREGADOS!")
listar()
print("--------------------")
'''




AUDIO_PRESSING = False # Representa o estado da captura de áudio
RUNNING = True 
TIME = 0



selected = 0




ENTRADA_AUDIO.start()
# Loop de gerenciamento de eventos
try:
    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    if sistema == "Windows":
                        os.system('cls')
                    else:
                        os.system('clear')
                if event.key == pygame.K_q:
                    AUDIO_PRESSING = True if not AUDIO_PRESSING else False
                    
                    if not AUDIO_PRESSING:
                        print("not", end=" ")
                    print("Listening!")
                elif event.key == pygame.K_f:
                    interact_text()

        roteiro.update()

        screen.display.fill('black')

        screen.update(TIME)
        # caixa_de_texto.draw_rect_alpha(screen.getDisplay())
        # caixa_de_texto.render_text(screen.getDisplay())


        pygame.display.flip()

        clock.tick(FPS)  # limits FPS to 60
        TIME += 1

except KeyboardInterrupt:
    pass
except Exception as e:
    print(str(e))

# Apaga arquivo de audio auxiliar
try:
    if sistema == "Windows":
        cmd = "del " + file_path
    else:
        cmd = "rm " + file_path
    os.system(cmd)
except Exception:
    pass

# Encerrar a gravação
print("Encerrando gravação.")

#stream.stop_stream()
#stream.close()
p.terminate()

# Encerra o pygame
pygame.quit()
