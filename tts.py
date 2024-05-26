import torch
from TTS.api import TTS

def tts(texto):
    #Get Device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    #Lista os modelos de TTS disponíveis
    print(TTS().list_models())

    #Iniciar TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    #Texto para fala e fala para arquivo
    tts.tts_to_file(text=texto, speaker_wav="D:\Senac\IA (Tito)\Yamete.wav", language="pt", file_path="output.wav")