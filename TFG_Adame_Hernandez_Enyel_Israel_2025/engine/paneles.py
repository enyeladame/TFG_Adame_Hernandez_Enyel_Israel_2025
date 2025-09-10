'''Módulo de control y generación gráfica de los paneles tanto de los controles como de las 
opciones al pausar el juego.'''

import pygame

#Ventana inferior donde se muestran los controles.
def panel_controles(screen, fuente, ancho, alto):
    rect=pygame.Rect(ancho//2-220, alto//2-160, 440,320)
    pygame.draw.rect(screen,(40,40,48),rect,border_radius=10)
    xbtn=pygame.Rect(rect.right-30,rect.top+8,22,22); pygame.draw.rect(screen,(200,50,50),xbtn,border_radius=4)
    screen.blit(fuente.render('CONTROLES',True,(255,255,255)),(rect.x+16,rect.y+12))
    lines=['Selecciona una acción en la izquierda.','Luego haz clic sobre un objetivo.','Algunas requieren ítem del inventario.']
    
    for i,l in enumerate(lines): 
        screen.blit(fuente.render(l,True,(235,235,235)),(rect.x+16,rect.y+48+i*28))
    
    return rect,xbtn

#Ventana modal que pausa la interacción con el resto del juego, abriendo las opciones y pausando la música.
def panel_opciones(screen, fuente, vol, ancho, alto):
    rect=pygame.Rect(ancho//2-220, alto//2-160, 440,320)
    pygame.draw.rect(screen,(40,40,48),rect,border_radius=10)
    xbtn=pygame.Rect(rect.right-30,rect.top+8,22,22); pygame.draw.rect(screen,(200,50,50),xbtn,border_radius=4)
    screen.blit(fuente.render('OPCIONES',True,(255,255,255)),(rect.x+16,rect.y+12))
    screen.blit(fuente.render(f'Volumen música: {vol}/10',True,(255,255,255)),(rect.x+16,rect.y+48))
    sliders=[]; 
    
    for i in range(11):
        r=pygame.Rect(rect.x+16+i*36, rect.y+84, 28,24); col=(0,200,0) if i<=vol else (80,80,80)
        pygame.draw.rect(screen,col,r,border_radius=4); sliders.append((r,i))
    
    btn_guardar=pygame.Rect(rect.x+16, rect.y+128, 180,36)
    btn_menu=pygame.Rect(rect.x+16, rect.y+176, 180,36)
    pygame.draw.rect(screen,(120,180,220),btn_guardar,border_radius=6)
    pygame.draw.rect(screen,(220,160,120),btn_menu,border_radius=6)
    screen.blit(fuente.render('Guardar partida...',True,(0,0,0)),(btn_guardar.x+12,btn_guardar.y+8))
    screen.blit(fuente.render('Salir al menú',True,(0,0,0)),(btn_menu.x+12,btn_menu.y+8))
    
    return rect,xbtn,sliders,btn_guardar,btn_menu
