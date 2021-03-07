#!/usr/bin/env python3

import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
import pyttsx3
import json
import core

#sintese de fala
engine = pyttsx3.init()


voices = engine.getProperty('voices')  
engine.setProperty('voice', voices[-2].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

q = queue.Queue()

def int_or_str(text):
    """Função auxiliar para análise de argumento."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """Isso é chamado (a partir de um thread separado) para cada bloco de áudio."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-f', '--filename', type=str, metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-m', '--model', type=str, metavar='MODEL_PATH',
    help='Path to the model')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

try:
    if args.model is None:
        args.model = "model"
    if not os.path.exists(args.model):
        print ("Baixe um modelo para o seu idioma em https://alphacephei.com/vosk/models")
        print ("e descompacte como 'modelo' na pasta atual.")
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile espera um int, sounddevice fornece um float:
        args.samplerate = int(device_info['default_samplerate'])

    model = vosk.Model(args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8192, device=args.device, dtype='int16',
                            channels=1, callback=callback):
            print('#' * 80)
            print('Pressione Ctrl + C para parar a gravação')
            print('#' * 80)

            rec = vosk.KaldiRecognizer(model, args.samplerate)
            while True:
                data = q.get()
                data = bytes(data)
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    result = json.loads(result)

                    if result is not None:
                        text = result['text']

                    print(text)
                    speak(text)

                    if text == 'que horas são' or text == 'me diga as horas':
                        speak(core.SystemInfo.get_time())
              
except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))