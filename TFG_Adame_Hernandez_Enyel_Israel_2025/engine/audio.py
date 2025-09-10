'''Sistema de audio que utiliza el subsistema pygame.mixer que nos permite reproducir música,
pausarla o reanudarla, y configurar el volumen a la que esta suena.'''

import pygame
_vol=5  #Volumen inicial.

#Diferentes procedimientos y funciones para controlar la música reproducida.
def iniciar_audio():
    try: pygame.mixer.init()
    except Exception: pass

def reproducir_musica(ruta, volumen=5, repetir=-1):
    ajustar_volumen(volumen)
    try:
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(_vol/10.0)
        pygame.mixer.music.play(repetir)
    except Exception: pass

def pausar_musica():
    try: pygame.mixer.music.pause()
    except Exception: pass

def reanudar_musica():
    try: pygame.mixer.music.unpause()
    except Exception: pass

def detener_musica():
    try: pygame.mixer.music.stop()
    except Exception: pass

def ajustar_volumen(v):
    global _vol; _vol=max(0,min(10,int(v)))
    try: pygame.mixer.music.set_volume(_vol/10.0)
    except Exception: pass

def obtener_volumen(): 
    return _vol
