import pyttsx3
engine = pyttsx3.init()


voices = engine.getProperty('voices')  

engine.setProperty('voice', voices[-2].id)

engine.say("Olá sou o jhow; no que posso te ajudar")
engine.runAndWait()