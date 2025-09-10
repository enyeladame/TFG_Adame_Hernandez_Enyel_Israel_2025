'''Programa principal para la ejecución de la DEMO. 
Trata el menú, paneles, música de fondo, acciones, invetario y barra de diálogo.
Inicializa pygame, dibuja la interfaz de usuario, procesa las entradas, carga los datos tipo
JSON, ejecuta la lógica de interacciones, inventario, combinaciones, diálogo, etc.'''

import os, json, pygame, sys, copy

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(__file__))  #Raiz del proyecto es el "padre" de la carpeta actual donde se encuentra demo.main.
if RAIZ_PROYECTO not in sys.path:
    sys.path.append(RAIZ_PROYECTO)

BASE_DIR = os.path.dirname(__file__)

from engine.recursos import configurar_carpeta_base, cargar_imagen, cargar_fuente, metricas #Gestor de recursos y métricas (fuentes/sonidos/imágenes)
from engine.audio import iniciar_audio, reproducir_musica, pausar_musica, reanudar_musica, detener_musica, ajustar_volumen, obtener_volumen #Sistema de audio/música.
from engine.menu import dibujar_menu, dibujar_opciones_menu #Pantalla de menú y las opciones.
from engine.paneles import panel_controles, panel_opciones  #Paneles mostrados durante la partida.
from engine.guardado import guardar_partida, cargar_partida #Guardado y carga del estado de la partida en archivo JSON.
from engine.combinaciones import puede_combinar #Combinaciones de items dentro del inventario.
from engine.scripting import ejecutar_scripts   #Ejecución de scrripts.
from engine.cursor import ocultar_cursor_sistema, cargar_cursor, dibujar_cursor #Control del cursor personalizado de la demo.
from engine.rendimiento import MedidorRendimiento   #Telemetría de rendimiento (FPS, eventos detectados, imágenes, etc.).

#Constantes de UI, areas de interacción, conjunto de acciones disponibles.
ANCHO, ALTO = 800, 620
AREA_JUEGO = pygame.Rect(0,0,800,500)
AREA_INV   = pygame.Rect(400,500,400,120)
ACCIONES = ['Abrir','Usar','Mirar','Hablar','Dar','Tomar','Combinar','Opciones']

#Carga de las rutas de audio del juego.
RUTA_MENU_OST  = os.path.join(BASE_DIR, 'assets', 'ost', 'Hazelwood - Coming Of Age (freetouse).mp3')
RUTA_JUEGO_OST = os.path.join(BASE_DIR, 'assets', 'ost', 'Lukrembo - Bored (freetouse).mp3')

#Devuelve true si el punto se encuentra dentro del polígono. En caso contrario false.
def _punto_en_poligono(pt, pts):
    x, y = pt
    inside = False
    n = len(pts)
    j = n - 1
    
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        #Cruce de una semirrecta horizontal.
        if ((yi > y) != (yj > y)):
            x_int = xi + (y - yi) * (xj - xi) / (yj - yi + 1e-12)
            if x < x_int:
                inside = not inside
        j = i
    
    return inside

#Comprueba si la posicion esta dentro de una figura.
def contiene_punto(fig, pos):
    #'Fig' puede ser una figura rectangular o poligonal regular/irregular.
    if 'poligono' in fig:
        return _punto_en_poligono(pos, fig['poligono'])
    if 'rect' in fig:
        x,y,w,h = fig['rect']
        return pygame.Rect(x,y,w,h).collidepoint(pos)
    
    return False

#Ayuda visual para el jugador/desarrollador de los interactuables.
def dibujar_figura(screen, fig, color, width=2):
    if 'poligono' in fig:
        pygame.draw.polygon(screen, color, fig['poligono'], width)
    elif 'rect' in fig:
        x,y,w,h = fig['rect']
        pygame.draw.rect(screen, color, pygame.Rect(x,y,w,h), width)

#Carga de datos desde los archivos JSON (habitaciones y recetas disponibles).
def cargar_datos(base):
    with open(os.path.join(base,'datos','habitaciones.json'),encoding='utf-8') as f: h=json.load(f)
    with open(os.path.join(base,'datos','recetas.json'),encoding='utf-8') as f: r=json.load(f)
    
    return h, r

#Dibuja la barra de diálogo, los cuadros de acciones, el inventario.
def dibujar_interfaz(screen, fuente, accion_sel, inventario, mensaje):
    #Franja inferior de 800x120 y la barra de diálogo.
    pygame.draw.rect(screen, (60,60,60), pygame.Rect(0, 500, 800, 120))
    pygame.draw.rect(screen, (0,0,0),   pygame.Rect(0, 500, 800, 26))
    if mensaje:
        screen.blit(fuente.render(mensaje[:110], True, (255,255,255)), (8, 503))
    
    #Base vertical para acciones/inventario debajo de la barra de diálogo.
    y_base = 500 + 26 + 6  # 532
    
    #'Acciones'
    w_btn, h_btn, vgap = 115, 26, 5
    cuadros = []
    for i, acc in enumerate(ACCIONES[:-1]):
        col, fil = i % 3, i // 3
        x = 10 + col * (w_btn + 10)
        y = y_base + fil * (h_btn + vgap)  #Los valores son 532, 563 y 594.
        r = pygame.Rect(x, y, w_btn, h_btn)
        pygame.draw.rect(screen, (120,200,255) if accion_sel==acc else (220,220,220), r, border_radius=4)
        screen.blit(fuente.render(acc, True, (0,0,0)), (r.x + 6, r.y + 4))
        cuadros.append((r, acc))
    
    #'Opciones' ocupa 2 columnas de la última fila por motivos esteticos.
    r_op = pygame.Rect(10 + 1*(w_btn+10), y_base + 2*(h_btn+vgap), w_btn*2 + 10, h_btn)
    pygame.draw.rect(screen, (120,200,255) if accion_sel=='Opciones' else (220,220,220), r_op, border_radius=4)
    screen.blit(fuente.render('Opciones', True, (0,0,0)), (r_op.x + 6, r_op.y + 4))
    cuadros.append((r_op, 'Opciones'))
    
    #Inventario (2 filas x 3 columnas = 6 items).
    #Área disponible para inventario debajo de la barra de diálogo desde y=532 hasta y=620 --> 88 px
    gap_filas = 4
    cel_h = (88 - gap_filas) // 2  #Total de 42
    cel_w = 60
    celdas = []

    for i in range(6):
        col, fil = i % 3, i // 3
        x = 400 + col*133 + 20
        y = y_base + fil * (cel_h + gap_filas)  #Filas en 532 y 578; 578 + 42 = 620.
        cel = pygame.Rect(x, y, cel_w, cel_h)
        pygame.draw.rect(screen, (235,235,235), cel, border_radius=4)
        if i < len(inventario):
            it = inventario[i]
            icon = cargar_imagen(os.path.join('assets','items', f'{it}.png'), True)
            icon = pygame.transform.smoothscale(icon, (40,40))
            #Centrar icono dentro de la celda.
            screen.blit(icon, (cel.x + (cel_w-40)//2, cel.y + (cel_h-40)//2))
            celdas.append((cel, it))
        else:
            celdas.append((cel, None))

    return cuadros, celdas

#Dibujo del fondo, puertas, objetos, interactuables, NPCs.
def dibujar_habitacion(screen, fuente, hab):
    fondo=cargar_imagen(hab['fondo'],True)
    fondo=pygame.transform.smoothscale(fondo,(800,500)); screen.blit(fondo,(0,0))

    for p in hab.get('puertas',[]): #Puertas (open = verde, closed = rojo).
        color = (120,200,120) if p['abierta'] else (200,80,80)
        dibujar_figura(screen, p, color, 3)
        label_pos = tuple(p['poligono'][0]) if 'poligono' in p else (p['rect'][0]+4, p['rect'][1]+4)
        screen.blit(fuente.render(p['id'], True, (255,255,255)), label_pos)

    for it in hab.get('interactuables',[]): #Interactuables (amarillos) + identificación.
        dibujar_figura(screen, it, (200,200,60), 2)
        label_pos = tuple(it['poligono'][0]) if 'poligono' in it else (it['rect'][0]+4, it['rect'][1]+4)
        screen.blit(fuente.render(it['id'], True, (20,20,20)), label_pos)

    for ob in hab.get('objetos_suelo',[]):  #Objetos, se dibuja su icono dentro de su recuadro.
        x,y,w,h=ob['rect']; icon=cargar_imagen(os.path.join('assets','items',f"{ob['id']}.png"),True)
        icon=pygame.transform.smoothscale(icon,(40,40)); screen.blit(icon,(x,y))

    if hab.get('npc'):  #Dibujo de los NPCs. Si falla la carga se utiliza un placeholder.
        npc=hab['npc']; x,y,w,h=npc['rect']; spr=cargar_imagen(os.path.join('assets','sprites','Abuela.png'),True)
        try: spr=pygame.transform.smoothscale(spr,(w,h)); screen.blit(spr,(x,y))
        except Exception: pygame.draw.rect(screen,(180,120,180),pygame.Rect(x,y,w,h))

#Ventana modal que muestra en una lista el contenido de un interactuable tipo contendor.
def ventana_contenedor(screen, fuente, cont):
    cx,cy,cw,ch=240,160,320,240; rect=pygame.Rect(cx,cy,cw,ch)
    pygame.draw.rect(screen,(30,30,34),rect,border_radius=10)
    xbtn=pygame.Rect(cx+8,cy+8,22,22); pygame.draw.rect(screen,(220,70,70),xbtn,border_radius=4)
    screen.blit(fuente.render(cont['id'],True,(255,255,255)),(cx+40,cy+10))
    filas=[]; yy=cy+50

    for it in cont.get('items',[]): #Una vez vacio ya no se puede abrir nuevamente.
        r=pygame.Rect(cx+20,yy,cw-40,26); pygame.draw.rect(screen,(70,70,78),r,border_radius=4)
        screen.blit(fuente.render(it,True,(255,255,255)),(r.x+8,r.y+4)); filas.append((r,it)); yy+=32
    
    return rect, xbtn, filas

#Lógica de la conversación con el NCP 'Abuela' y las diferentes "reacciones" a items y flags que se encargan de secuenciar la aventura.
def dialogo_abuela(flags, accion, item=None):
    if accion=='Hablar':    #Hablamos con NPC en diferentes puntos de la aventura (determinado por las flags).
        if not flags.get('manta_entregada'): return 'Abuela: ¿Me trairías la manta de mi armario? La llave de mi cuarto la perdí por la casa.'
        if not flags.get('control_entregado'): return 'Abuela: Gracias por la manta. El control necesita baterias. ¿Podrías ponerselas y darmelo?'
        if not flags.get('sandwich_entregado'): return 'Abuela: Me apetece un sandwich de bacon y queso. ¿Me lo puedes preparar por favor?'
        return 'Abuela: Gracias por todo.'
    
    if accion=='Dar':   #Damos diferentes items a NCP.
        if item=='Manta' and not flags.get('manta_entregada'):
            flags['manta_entregada']=True; return 'Abuela: ¡Qué calentita! Gracias. El control todavia necesita baterias. Cuando puedas cariño.'
        if item=='Control_1' and flags.get('manta_entregada') and not flags.get('control_entregado'):
            flags['control_entregado']=True; return 'Abuela: ¡Funciona! Ahora solo te pido por favor algo de comer.'
        if item=='SandwichBaconQueso' and flags.get('control_entregado') and not flags.get('sandwich_entregado'):
            flags['sandwich_entregado']=True; flags['final_logrado']=True; return 'Abuela: ¡Delicioso! Eso es todo cariño. Toma este billete para que te compres algo. Gracias por la ayuda.'
    
    return 'Abuela: ¿... y esto para qué hijo?' #Caso de objeto equivocado.

#Inicializa Pygame y el audio, muestra el menú, ejecuta la partida, procesamiento de eventos, dibujo de escena/UserInterface, gestion de inventario, ejecución de scripts declarativos.
def run_demo():
    pygame.init(); iniciar_audio()
    icono_aplicado = False
    
    #Aplicación del icono de la ventana. Se reescala de hacer falta.
    for ruta_rel in [("sprites", "Icono.png"), ("assets", "sprites", "Icono.png")]:
        ruta_abs = os.path.join(BASE_DIR, *ruta_rel)
        if os.path.exists(ruta_abs):
            try:
                surf = pygame.image.load(ruta_abs)
                if surf.get_width() != 32 or surf.get_height() != 32:
                    surf = pygame.transform.smoothscale(surf, (32, 32))
                pygame.display.set_icon(surf)
                icono_aplicado = True
                break
            except Exception: pass
    
    #Ventana principal.
    screen=pygame.display.set_mode((ANCHO,ALTO)); pygame.display.set_caption('DEMO - Motor SCUMM TFG')
    
    #Configuramos la carpeta base para la gestion de recursos y carga de la fuente y del cursor personalizado.
    configurar_carpeta_base(BASE_DIR); fuente=cargar_fuente(os.path.join('assets','fuentes','Roboto-Regular.ttf'),16)
    ocultar_cursor_sistema(); img_cur=cargar_imagen(os.path.join('assets','cursor','Cursor.png'),True)
    configurar_carpeta_base(BASE_DIR)
    fuente = cargar_fuente(os.path.join('assets','fuentes','Roboto-Regular.ttf'),16)
    
    #Reproducción de música en el menú.
    try:
        reproducir_musica(RUTA_MENU_OST, obtener_volumen(), -1)
    except Exception: pass

    habitaciones_base, recetas = cargar_datos(BASE_DIR) #Carga los datos de habitaciones.json y recetas.json.
    
    #Estado del juego durante el runtime/ejecución.
    habitaciones = {}
    habitacion_actual = ''
    inventario = []
    flags = {}
    accion_sel = None
    mensaje = ''
    panel_op = False
    panel_ctrl = False
    cont_abierto = None
    sel_usar = None
    sel_dar = None
    sel_comb = []

    #Vuelve a inicializar todos los valores y flags para volver al inicio de la partida.
    def reiniciar_partida():
        nonlocal habitaciones, habitacion_actual, inventario, flags
        nonlocal accion_sel, mensaje, panel_op, panel_ctrl, cont_abierto
        nonlocal sel_usar, sel_dar, sel_comb

        habitaciones = copy.deepcopy(habitaciones_base)
        habitacion_actual='Habitacion_1'; inventario=[]; flags={'mensaje_inicial':True}
        accion_sel=None; mensaje='¡Tu abuela te llama a la sala para pedirte ayuda!'
        panel_op=False; panel_ctrl=False; cont_abierto=None
        sel_usar=None; sel_dar=None; sel_comb=[]

    #Métricas y control del reloj para medir el tiempo de ejecución.
    med=MedidorRendimiento(); reloj=pygame.time.Clock()
    en_menu=True; en_opciones=False; jugando=False; volumen=5

    #Control de cambio de habitación actual a la seleccionada. 
    def cambio_hab(n):
        nonlocal habitacion_actual, mensaje, sel_usar, sel_dar, sel_comb, cont_abierto
        habitacion_actual=n; mensaje=''; sel_usar=None; sel_dar=None; sel_comb.clear(); cont_abierto=None

    #Bucle principal del juego.
    while True:
        ev=pygame.event.get()
        #Menu principal.
        if en_menu:
            if not en_opciones:
                #Dibujo del menu inicial.
                botones=dibujar_menu(screen, fuente, 'DEMO - Aventura SCUMM', ANCHO, ALTO)
                dibujar_cursor(screen, img_cur, pygame.mouse.get_pos())
                pygame.display.flip()
                for e in ev:
                    if e.type==pygame.QUIT: #Al cerrar la ventana se imprime el resumen de métricas.
                        print('[RESUMEN DEMO]', med.finalizar(), 'Métricas:', metricas); return
                    if e.type==pygame.MOUSEBUTTONDOWN:
                        pos=pygame.mouse.get_pos()
                        for r,lab in botones:
                            if r.collidepoint(pos):
                                if lab=='Jugar': 
                                    reiniciar_partida(); #Comienzo de partida nueva.
                                    en_menu=False; jugando=True; 
                                    med = MedidorRendimiento(); med.iniciar()
                                    #Volvemos a la múysica del juego.
                                    try:
                                        reproducir_musica(RUTA_JUEGO_OST, obtener_volumen(), -1)
                                    except Exception: pass

                                elif lab=='Cargar Partida':
                                    data=cargar_partida()   #Carga del estado de la partida desde el archivo JSON.
                                    if data:
                                        habitaciones = copy.deepcopy(data['habitaciones'])
                                        habitacion_actual = data['habitacion_actual']
                                        inventario = data.get('inventario', [])
                                        flags = data.get('flags', {})
                                        accion_sel = None; mensaje = ''; panel_op = panel_ctrl = False
                                        cont_abierto = None; sel_usar = sel_dar = None; sel_comb = []
                                        en_menu = False; jugando = True
                                        med = MedidorRendimiento(); med.iniciar()
                                        try:
                                            reproducir_musica(RUTA_JUEGO_OST, obtener_volumen(), -1)
                                        except Exception: pass

                                elif lab=='Opciones': #Entramos al submenu de opciones.
                                    en_opciones=True
                                elif lab=='Salir':  #Finalizamos la ejecución de la demo.
                                    print('[RESUMEN DEMO]', med.finalizar(), 'Métricas:', metricas); return
            else:
                #Opciones dentro del menú principal.
                sliders, volver = dibujar_opciones_menu(screen, fuente, volumen, ANCHO, ALTO)
                dibujar_cursor(screen, img_cur, pygame.mouse.get_pos())
                pygame.display.flip()
                for e in ev:
                    if e.type==pygame.QUIT:
                        print('[RESUMEN DEMO]', med.finalizar(), 'Métricas:', metricas); return
                    if e.type==pygame.MOUSEBUTTONDOWN:
                        pos=pygame.mouse.get_pos()
                        if volver.collidepoint(pos):
                            en_opciones=False
                        for r,val in sliders:
                            if r.collidepoint(pos): volumen=val; ajustar_volumen(val)
        #Juego.
        elif jugando:
            #Dibujamos la escena.
            hab=habitaciones[habitacion_actual]
            dibujar_habitacion(screen, fuente, hab)
            cuadros, celdas = dibujar_interfaz(screen, fuente, accion_sel, inventario, mensaje)
            if panel_ctrl:
                rect,xbtn = panel_controles(screen, fuente, ANCHO, ALTO)
            if panel_op:
                rect_op, xbtn_op, sliders, btn_guardar, btn_menu = panel_opciones(screen, fuente, obtener_volumen(), ANCHO, ALTO)
            
            #Ventana del contenedor abierta.
            cont_rect = cont_xbtn = None
            cont_filas = []
            
            if cont_abierto:
                cont_rect, cont_xbtn, cont_filas = ventana_contenedor(screen, fuente, cont_abierto)
            
            #Cursor personalizado.
            dibujar_cursor(screen, img_cur, pygame.mouse.get_pos())
            pygame.display.flip()

            #Procesamiento de eventos en base a las entradas del usuario/jugador.
            ev_count=0
            for e in ev:
                ev_count+=1
                if e.type==pygame.QUIT: #En caso de cerrar el juego.
                    print('[RESUMEN DEMO]', med.finalizar(), 'Métricas:', metricas); return
                if e.type==pygame.MOUSEBUTTONDOWN:
                    pos=pygame.mouse.get_pos()
                    if panel_ctrl:
                        rect,xbtn = panel_controles(screen, fuente, ANCHO, ALTO)
                        if xbtn.collidepoint(pos): panel_ctrl=False
                        continue
                    if panel_op:    #Panel 'Opciones' abierto.
                        rect_op, xbtn_op, sliders, btn_guardar, btn_menu = panel_opciones(screen, fuente, obtener_volumen(), ANCHO, ALTO)
                        if xbtn_op.collidepoint(pos):
                            panel_op=False; reanudar_musica(); continue
                        for r,val in sliders:
                            if r.collidepoint(pos): ajustar_volumen(val)
                        if btn_guardar.collidepoint(pos):
                            ok,_=guardar_partida({'habitaciones':habitaciones,'habitacion_actual':habitacion_actual,'inventario':inventario,'flags':flags})
                            mensaje='Partida guardada.' if ok else 'No se pudo guardar.'; panel_op=False; continue
                        if btn_menu.collidepoint(pos):  #Vuelta al menú principal.
                            en_menu=True; jugando=False; en_opciones=False; panel_op = False
                            try:
                                reproducir_musica(RUTA_MENU_OST, obtener_volumen(), -1)
                            except Exception: pass
                            continue

                    #Selección de la acción.
                    for r,acc in cuadros:
                        if r.collidepoint(pos): accion_sel=acc; 
                        if acc=='Opciones' and r.collidepoint(pos): panel_op=True; pausar_musica()
                    
                    #Interacción con la ventana del contenedor SOLO si esta está abierta.
                    if cont_abierto and cont_rect:
                        #Opción de cerrar con el cuadro rojo.
                        if cont_xbtn and cont_xbtn.collidepoint(pos):
                            cont_abierto = None
                            continue

                        #Tomar items dentro de la lista.
                        if accion_sel == 'Tomar' and cont_filas:
                            for r, itn in cont_filas:
                                if r.collidepoint(pos):
                                    if len(inventario) >= 6:
                                        mensaje = 'Inventario lleno.'
                                    else:
                                        inventario.append(itn)
                                        cont_abierto['items'].remove(itn)
                                        cont_abierto['vacio'] = len(cont_abierto['items']) == 0
                                        mensaje = f'Has tomado {itn}.'
                                        # opcional: cerrar si ya quedó vacío
                                        if cont_abierto['vacio']:
                                            cont_abierto = None
                                    continue

                        if cont_rect.collidepoint(pos):  #Evita que el clic "atraviese" la ventana hacia la escena
                            continue

                    #Detección en área del juego.
                    if pygame.Rect(0,0,800,500).collidepoint(pos):
                        tar=None
                        #Puertas
                        for p in hab.get('puertas', []):
                            if contiene_punto(p, pos):
                                tar = ('puerta', p)
                                break
                        #Interactuables/Contenedores.
                        if not tar:
                            for it in hab.get('interactuables', []):
                                if contiene_punto(it, pos):
                                    tar = ('inter', it)
                                    break
                        #Objetos en el escenario.
                        if not tar:
                            for ob in hab.get('objetos_suelo', []):
                                if contiene_punto(ob, pos):
                                    tar = ('obj', ob)
                                    break
                        #NPCs invisibles.
                        if not tar and hab.get('npc'):
                            if contiene_punto(hab['npc'], pos):
                                tar = ('npc', hab['npc'])
                        if not accion_sel: mensaje='Selecciona una acción.'
                        else:
                            t = tar[0] if tar else None
                            if accion_sel=='Mirar':
                                if tar:
                                    if t=='puerta': mensaje=f"Es la {tar[1]['id']}."
                                    elif t=='inter':
                                        estado = "Vacio" if tar[1].get('vacio') else "Puede contener algo."
                                        mensaje = f"{tar[1]['id']}: {estado}"
                                    elif t=='obj': mensaje=f"Ves {tar[1]['id']} en el suelo."
                                else: mensaje='No ves nada interesante.'
                            elif accion_sel=='Hablar':
                                if hab.get('npc'): mensaje = dialogo_abuela(flags,'Hablar')
                                else: mensaje='No hay nadie con quien hablar.'
                            elif accion_sel=='Tomar':
                                if t=='obj':
                                    itn=tar[1]['id']
                                    if len(inventario)>=6: mensaje='Inventario lleno.'
                                    else:
                                        inventario.append(itn); hab['objetos_suelo'].remove(tar[1]); mensaje=f'Has tomado {itn}.'
                                elif t=='inter' and tar[1]['tipo']=='contenedor':
                                    cont_abierto = None if tar[1].get('vacio') else tar[1]
                                    if not cont_abierto: mensaje='Está vacío.'
                                else: mensaje='No hay nada que tomar.'
                            elif accion_sel=='Abrir':
                                if t=='puerta':
                                    p=tar[1]
                                    if p['abierta']: habitacion_actual=p['destino']; mensaje=''
                                    else: mensaje='Está cerrada.'
                                elif t=='inter':
                                    it=tar[1]
                                    if it['tipo']=='contenedor':
                                        cont_abierto = None if it.get('vacio') else it
                                        if not cont_abierto: mensaje='Está vacío.'
                                    else: mensaje=f'Abres {it["id"]}, nada especial.'
                                else: mensaje='No hay nada que abrir.'
                            elif accion_sel=='Usar':
                                if sel_usar is None: mensaje='Selecciona un ítem del inventario.'
                                else:
                                    ctx={'inventario':inventario,'flags':flags,'cambio_habitacion':cambio_hab,'mensaje':lambda t:None}
                                    obj_id = tar[1]['id'] if tar else None
                                    texto = ejecutar_scripts(hab,'usar',ctx,objetivo=obj_id,item=sel_usar)
                                    if texto: mensaje=texto
                                    sel_usar=None
                            elif accion_sel=='Dar':
                                if hab.get('npc') and hab['npc']['id']=='Abuela':
                                    if sel_dar is None: mensaje='Selecciona un ítem para dar a Abuela.'
                                    else:
                                        texto=dialogo_abuela(flags,'Dar',sel_dar); mensaje=texto
                                        if sel_dar in inventario and sel_dar in ['Manta','Control_1','SandwichBaconQueso']:
                                            inventario.remove(sel_dar)
                                        if flags.get('final_logrado') and 'Billete' not in inventario:
                                            if len(inventario)<6: 
                                                inventario.append('Billete')
                                            else: mensaje = texto + 'Inventario demasiado lleno! No puedes recibir el nuevo objeto.'
                                        sel_dar=None
                                else: mensaje='No hay a quién dárselo.'
                            elif accion_sel=='Combinar':
                                mensaje='Elige dos ítems del inventario para combinar.'

                    #Click dentro del inventario.
                    if pygame.Rect(400,500,400,120).collidepoint(pos):
                        for cel,itn in celdas:
                            if cel.collidepoint(pos) and itn:
                                if accion_sel=='Usar': sel_usar=itn; mensaje=f'Vas a usar {itn}. Elige un objetivo.'
                                elif accion_sel=='Dar': sel_dar=itn; mensaje=f'Vas a dar {itn} a un NPC.'
                                elif accion_sel=='Combinar':
                                    sel_comb.append(itn)
                                    if len(sel_comb)==2:
                                        #Combinación de items independiente del orden de selección.
                                        res = puede_combinar(sel_comb[0], sel_comb[1], recetas)
                                        if res:
                                            try: inventario.remove(sel_comb[0])
                                            except: pass
                                            try: inventario.remove(sel_comb[1])
                                            except: pass
                                            if len(inventario)<6: inventario.append(res); mensaje=f'Has creado {res}.'
                                            else: mensaje='No hay espacio para el resultado.'
                                        else: mensaje='Esa combinación no funciona.'
                                        sel_comb.clear()
                                elif accion_sel=='Mirar': mensaje=f'Es {itn}.'

            #Registro del rendimiento.
            med.registrar(inventario, len(ev))

#Main que se encarga de ejecutar la demo.
if __name__=='__main__':
    run_demo()