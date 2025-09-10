'''Módulo que cambia el cursor proporcionado por el Sistema Operativo SO y dibuja un sprite
de 32x32 con su hotspot alineado en (0,0) del sprite. Ayuda a mejorar la cohesión estética
y a la retroalimentación visual.'''

import pygame
from .recursos import cargar_imagen

#No mostramos el cursor del SistemaOperativo SO dentro de la ventana del programa.
def ocultar_cursor_sistema():
    try: pygame.mouse.set_visible(False)
    except Exception: pass

#Obtenemos el script del cursor personalizado.
def cargar_cursor(ruta): 
    return cargar_imagen(ruta, True)

#Mostramos el script del cursor personalizado encima de la ventana, estableciendo su hotspot en (0,0) de su imagen.
def dibujar_cursor(screen,img,pos,hotspot=(0,0)):
    if img: 
        screen.blit(img,(pos[0]-hotspot[0], pos[1]-hotspot[1]))
