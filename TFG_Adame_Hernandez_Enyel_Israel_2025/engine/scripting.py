'''Scripting. Se encarga de la ejecucion de reglas de acciones junto a un contexto determinado
por las flags, el inventario disponible, etc. Permite el control de la lógica de flags, items, mensajes 
obtenidos, etc.'''

#Conjunto de reglas estilo SCUMM. Permite separar el motor de la lógica concreta de la demo.
def ejecutar_scripts(hab, trigger, ctx, objetivo=None, item=None):
    salida=[]

    for s in hab.get('scripts',[]):
        if s.get('trigger')!=trigger: 
            continue

        if s.get('objetivo') and s['objetivo']!=objetivo: 
            continue

        if s.get('item') and s['item']!=item: 
            continue

        res = s.get('resultado',{})

        if 'mensaje' in res: 
            salida.append(res['mensaje'])

        if 'set_flag' in res: 
            ctx['flags'][res['set_flag']]=True

        if 'unset_flag' in res: 
            ctx['flags'].pop(res['unset_flag'],None)

        if 'eliminar_item' in res:
            try: ctx['inventario'].remove(res['eliminar_item'])
            except ValueError: pass

        if 'añadir_item' in res:
            if len(ctx['inventario'])<6: ctx['inventario'].append(res['añadir_item'])
        
        if 'abrir_puerta' in res:
            pid=res['abrir_puerta']
            for p in hab.get('puertas',[]): 
                if p['id']==pid: p['abierta']=True
        
        if 'cambiar_habitacion' in res:
            ctx['cambio_habitacion'](res['cambiar_habitacion'])

    return '\n'.join(salida)
