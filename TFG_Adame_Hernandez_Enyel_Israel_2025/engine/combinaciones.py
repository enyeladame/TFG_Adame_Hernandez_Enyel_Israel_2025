'''Módulo de combinación de items utilizando las combinaciones aceptadas dentro del archivo
'recetas', diseñado conmutativamente para pares de objetos (A + B = B + A).'''

#Hace uniformes los objetos obtenidos quitando espacios en blanco y pasando todo a minúscula.
def normalizar(n): 
    return n.strip().lower()

#Garantiza que, sin importar el orden, obtiene como resultado, si hay una coincidencia dentro de recetas, el objeto esperado.
def puede_combinar(a,b,recetas):
    A,B=normalizar(a),normalizar(b)
    
    for r in recetas:
        ins=[normalizar(x) for x in r.get('ingredientes',[])]
        if len(ins)==2 and A in ins and B in ins and A!=B: 
            return r.get('resultado')
        
    return None
