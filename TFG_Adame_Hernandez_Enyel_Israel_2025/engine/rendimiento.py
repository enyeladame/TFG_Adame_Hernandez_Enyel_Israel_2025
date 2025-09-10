'''Módulo simple que mide el rendimiento durante la ejecución de la DEMO, con frames por
segundo, eventos detectados por frame, cantidad de objetos máximos en el inventario y la
duración de la ejecución. Este resumen se imprime por consola/terminal al salir o cerrar
la ejecución.'''

import time

class MedidorRendimiento:
    #Inicializa la telemetría.
    def __init__(self):
        self.t0=None; self.frames=0; self.eventos=0; self.max_inv=0
    
    #Comienzo del proceso de medición.
    def iniciar(self):
        import time; self.t0=time.perf_counter()
    
    #Control y actualización de los datos y sus valores.
    def registrar(self, inv, ev):
        self.frames+=1; self.eventos+=ev; self.max_inv=max(self.max_inv,len(inv) if inv else 0)
    
    #Finalización de la medición telemetríca y impresión de los resultados por consola/terminal.
    def finalizar(self):
        import time; t1=time.perf_counter(); dt=max(1e-6,(t1-(self.t0 or t1)))
        fps=self.frames/dt if dt>0 else 0.0
        
        return {'duracion_s':round(dt,2),'frames':self.frames,'fps_medio':round(fps,1),'eventos':self.eventos,'max_inventario':self.max_inv}
