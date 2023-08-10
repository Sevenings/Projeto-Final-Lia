import speech_recognition as sr
import os

lang = 'pt'

# Criar um reconhecedor de voz
r = sr.Recognizer()
# Abrir o microfone para capturar áudio
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
