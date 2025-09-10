'''Módulo de recursos que se encarga de la carga de imágenes, fuentes, la resolución de 
rutas de direcciones.'''

import os, pygame

_carpeta_base=None; _cache_img={}; _cache_font={}; _cache_sfx={}
metricas={'imagenes':0,'fuentes':0,'sonidos':0}

#Fija la ráiz de los recursos desde donde se obtienen.
def configurar_carpeta_base(c): 
    global _carpeta_base; _carpeta_base=c

#Normaliza la ruta obtenida.
def _abs(r): 
    return os.path.join(_carpeta_base,r) if _carpeta_base and not os.path.isabs(r) else r

#Obtiene la imágen para ser usada como superficie. En caso de fallo se utilizará un "placeholder".
def cargar_imagen(r,alpha=True):
    R=_abs(r)
    if R in _cache_img: return _cache_img[R]
    try:
        img=pygame.image.load(R); img=img.convert_alpha() if alpha else img.convert()
        _cache_img[R]=img; metricas['imagenes']+=1; return img
    except Exception:
        s=pygame.Surface((64,64), pygame.SRCALPHA); s.fill((200,50,50,255)); _cache_img[R]=s; return s

#Obtiene la fuente utilizada para la letra en el programa y UserInterface.
def cargar_fuente(r,tam):
    k=(r,tam)
    if k in _cache_font: return _cache_font[k]
    try:
        R=_abs(r); f=pygame.font.Font(R,tam)
    except Exception:
        f=pygame.font.SysFont('Arial',tam)
    _cache_font[k]=f; metricas['fuentes']+=1; return f

#Obtiene la música/sonidos.
def cargar_sonido(r):
    R=_abs(r)
    if R in _cache_sfx: return _cache_sfx[R]
    try:
        s=pygame.mixer.Sound(R); _cache_sfx[R]=s; metricas['sonidos']+=1; return s
    except Exception:
        return None
