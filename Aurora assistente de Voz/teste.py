import speech_recognition as sr
import os

import pygame
from pygame.locals import *

lang = 'pt'





def OuvirMicrofone()
    r = sr.Recognizer()
    with sr.Microphone() as source:
        os.system('clear')
        while True:
            # Definir microfone como fonte de áudio
            audio = r.listen(source)
            try:
                comando = r.recognize_google(audio, language=lang)
                print(comando)
            except sr.exceptions.UnknownValueError:
                print("Não reconheci")




