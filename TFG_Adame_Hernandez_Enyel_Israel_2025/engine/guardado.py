'''Módulo con los componentes necesarios para el guardado y cargado del estado mutable del
juego (inventario, flags, habitaciones/sala actual, etc.)'''

import json, os

#Guardamos un núcleo mínimo para la persistencia de los valores, lo que serializa el inventario, flags, habitaciones, habitacion actual, etc.
def guardar_partida(estado, ruta=None):
    if ruta is None:
        try:
            import tkinter as tk
            from tkinter import filedialog
            r=tk.Tk(); r.withdraw()
            ruta=filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('Guardado','*.json')], title='Guardar partida...')
            r.destroy()
        except Exception: ruta='partida.json'
    
    if not ruta: return False, None
    with open(ruta,'w',encoding='utf-8') as f: json.dump(estado,f,ensure_ascii=False,indent=2)
    return True, ruta

#Función que establece el estado actual de la partida como uno guardado y descrito en un archivo .JSON.
def cargar_partida(ruta=None):
    if ruta is None:
        try:
            import tkinter as tk
            from tkinter import filedialog
            r=tk.Tk(); r.withdraw()
            ruta=filedialog.askopenfilename(filetypes=[('Guardado','*.json')], title='Cargar partida...')
            r.destroy()
        except Exception: return None

    if not ruta or not os.path.exists(ruta): return None
    with open(ruta,'r',encoding='utf-8') as f: return json.load(f)
