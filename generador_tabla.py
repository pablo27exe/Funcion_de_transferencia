"""
Generador de tabla de estados
"""
from utils import obtener_nombre_estado, obtener_nombre_valvula


class GeneradorTabla:
    
    def __init__(self, interprete):
        self.interprete = interprete
        self.cilindros = interprete.obtener_cilindros_ordenados()
        self.estados = interprete.obtener_estados_por_fase()
        self.activos = interprete.obtener_cilindros_activos_por_fase()
        self.num_fases = len(interprete.fases)
    
    def generar_datos_tabla(self) -> dict:
        """
        Genera datos estructurados para la tabla
        Retorna dict con:
        - headers: ['', '1', '2', '3', ...]
        - filas: lista de diccionarios {nombre_fila: [...valores]}
        """
        # Encabezados: columnas de fases
        headers = [''] + [str(i) for i in range(1, self.num_fases + 1)]
        
        filas = []
        
        # Filas de cilindros (A, B, C...)
        for cilindro in self.cilindros:
            fila = {'nombre': cilindro, 'valores': [], 'tipo': 'cilindro'}
            
            # Por cada fase (excluyendo fase 0)
            for fase_num in range(1, self.num_fases + 1):
                # Verificar si este cilindro está activo en esta fase
                esta_activo = cilindro in self.activos.get(fase_num, [])
                fila['valores'].append({
                    'valor': '',
                    'activo': esta_activo
                })
            
            filas.append(fila)
        
        # Filas de estados SW (Work)
        for cilindro in self.cilindros:
            fila = {'nombre': obtener_nombre_estado(cilindro, True), 'valores': [], 'tipo': 'estado'}
            
            for fase_num in range(1, self.num_fases + 1):
                estado_extendido = self.estados[cilindro][fase_num]
                esta_activo = cilindro in self.activos.get(fase_num, [])
                
                fila['valores'].append({
                    'valor': obtener_nombre_estado(cilindro, True) if estado_extendido else '',
                    'activo': esta_activo and estado_extendido
                })
            
            filas.append(fila)
        
        # Filas de estados SH (Home)
        for cilindro in self.cilindros:
            fila = {'nombre': obtener_nombre_estado(cilindro, False), 'valores': [], 'tipo': 'estado'}
            
            for fase_num in range(1, self.num_fases + 1):
                estado_contraido = not self.estados[cilindro][fase_num]
                esta_activo = cilindro in self.activos.get(fase_num, [])
                
                fila['valores'].append({
                    'valor': obtener_nombre_estado(cilindro, False) if estado_contraido else '',
                    'activo': esta_activo and estado_contraido
                })
            
            filas.append(fila)
        
        # Filas de válvulas Y
        for cilindro in self.cilindros:
            # YW (válvula Work)
            fila_yw = {'nombre': obtener_nombre_valvula(cilindro, True), 'valores': [], 'tipo': 'valvula'}
            # YH (válvula Home)
            fila_yh = {'nombre': obtener_nombre_valvula(cilindro, False), 'valores': [], 'tipo': 'valvula'}
            
            for fase_num in range(1, self.num_fases + 1):
                esta_activo = cilindro in self.activos.get(fase_num, [])
                
                if esta_activo:
                    # Determinar qué válvula se activa
                    fase_obj = self.interprete.fases[fase_num - 1]
                    accion = None
                    for c, a in fase_obj.movimientos:
                        if c == cilindro:
                            accion = a
                            break
                    
                    if accion == '+':  # Extender -> YW activa
                        fila_yw['valores'].append({
                            'valor': obtener_nombre_valvula(cilindro, True),
                            'activo': True
                        })
                        fila_yh['valores'].append({
                            'valor': '',
                            'activo': False
                        })
                    else:  # Contraer -> YH activa
                        fila_yw['valores'].append({
                            'valor': '',
                            'activo': False
                        })
                        fila_yh['valores'].append({
                            'valor': obtener_nombre_valvula(cilindro, False),
                            'activo': True
                        })
                else:
                    fila_yw['valores'].append({'valor': '', 'activo': False})
                    fila_yh['valores'].append({'valor': '', 'activo': False})
            
            filas.append(fila_yw)
            filas.append(fila_yh)
        
        return {
            'headers': headers,
            'filas': filas
        }