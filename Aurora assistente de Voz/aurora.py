import speech_recognition as sr
import os

correcoes = {
    'home': '~',
    'cd-rom': 'cd ~'
}

def traduzir(string, dicionario):
    output = string.split()
    for w in range(len(output)):
        word = output[w]
        if word in dicionario:
            output[w] = dicionario[word]
    return ' '.join(output)


# Criar um reconhecedor de voz
r = sr.Recognizer()

# Abrir o microfone para capturar áudio
with sr.Microphone() as source:
    while True:
        print("Diga seu comando> ")

        # Definir microfone como fonte de áudio
        audio = r.listen(source)
        try:
            comando = r.recognize_google(audio, language='en')
            comando = comando.lower()
            comando = traduzir(comando, correcoes)

            if input(f"Deseja executar: '{comando}' ? [s/n] ") == 's':
                os.system(comando)
        except sr.exceptions.UnknownValueError:
            print("Não reconheci")
