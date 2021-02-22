import speech_recognition as sr #Biblioteca para rec. de voz (transcreve fala em texto)

r = sr.Recognizer()

def main():
  try:
    while True:
      with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source) # Ajustando ruído ambiente
        audio = r.listen(source) # Extrai áudio do microfone
        speech = r.recognize_google(audio, language='pt-BR') #transcrevendo fala em texto com api da Google
        print('Você: ', speech)
  except sr.UnknownValueError:
        print('Erro de reconhecimento de fala')

if __name__ == "__main__":
    main()