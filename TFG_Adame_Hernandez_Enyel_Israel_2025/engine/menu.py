'''Control de la representación gráfica del menú principal, además de las opciones disponibles,
configuración (volumen), cargado de partida y salida del programa.'''

import pygame

def dibujar_menu(screen, fuente, titulo, ancho, alto):
    screen.fill((18,18,22)); #Otra forma sería screen.blit(fuente.render(titulo,True,(255,255,255)),(20,20))
    botones=[]; labels=['Jugar','Cargar Partida','Opciones','Salir']
    
    for i,txt in enumerate(labels):
        r=pygame.Rect(ancho//2-140,160+i*70,280,50)
        pygame.draw.rect(screen,(90,160,255),r,border_radius=8)
        screen.blit(fuente.render(txt,True,(0,0,0)),(r.x+20,r.y+12))
        botones.append((r,txt))

    return botones

def dibujar_opciones_menu(screen, fuente, volumen, ancho, alto):
    screen.fill((22,22,26)); screen.blit(fuente.render('Opciones',True,(255,255,255)),(20,20))
    screen.blit(fuente.render(f'Volumen música: {volumen}/10',True,(255,255,255)),(20,70))
    sliders=[]; base=20

    for i in range(11):
        r=pygame.Rect(base+i*30,110,22,24); col=(0,200,0) if i<=volumen else (80,80,80)
        pygame.draw.rect(screen,col,r,border_radius=4); sliders.append((r,i))

    volver=pygame.Rect(20,150,120,40); pygame.draw.rect(screen,(220,120,120),volver,border_radius=6)
    screen.blit(fuente.render('Volver',True,(0,0,0)),(volver.x+16,volver.y+8))

    return sliders, volver
