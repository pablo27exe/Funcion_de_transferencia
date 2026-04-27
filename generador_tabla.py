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
        """
        headers = ['Cilindro'] + [f'Fase {i}' for i in range(1, self.num_fases + 1)]
        
        filas = []
        
        # 1. Filas de cilindros (A, B, C...)
        for cilindro in self.cilindros:
            fila_cilindro = {'nombre': cilindro, 'valores': [], 'tipo': 'cilindro'}
            
            for fase_num in range(1, self.num_fases + 1):
                estado = self.estados[cilindro][fase_num]  # True=SW, False=SH
                esta_activo = cilindro in self.activos.get(fase_num, [])
                
                if estado:  # Extendido (SW)
                    valor = obtener_nombre_estado(cilindro, True)  # Sin paréntesis
                else:  # Contraído (SH)
                    valor = obtener_nombre_estado(cilindro, False)  # Sin paréntesis
                
                fila_cilindro['valores'].append({
                    'valor': valor,
                    'activo': esta_activo
                })
            
            filas.append(fila_cilindro)
        
        # 2. Una sola fila para todas las válvulas al final
        fila_valvulas = {'nombre': 'Válvulas', 'valores': [], 'tipo': 'valvulas'}
        
        for fase_num in range(1, self.num_fases + 1):
            valvulas_texto = []
            
            # Buscar todos los cilindros activos en esta fase
            cilindros_activos = self.activos.get(fase_num, [])
            
            for cilindro in cilindros_activos:
                fase_obj = self.interprete.fases[fase_num - 1]
                for c, accion in fase_obj.movimientos:
                    if c == cilindro:
                        if accion == '+':
                            valvulas_texto.append(f"YW{c}")  # Sin paréntesis
                        else:
                            valvulas_texto.append(f"YH{c}")  # Sin paréntesis
                        break
            
            # Unir múltiples válvulas con coma si hay más de una
            valor = ', '.join(valvulas_texto) if valvulas_texto else ''
            
            fila_valvulas['valores'].append({
                'valor': valor,
                'activo': len(valvulas_texto) > 0
            })
        
        filas.append(fila_valvulas)
        
        return {
            'headers': headers,
            'filas': filas
        }