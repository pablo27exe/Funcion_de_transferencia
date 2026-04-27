"""
Intérprete de funciones neumáticas
"""

class Fase:
    def __init__(self, numero: int, movimientos: list):
        """
        numero: número de fase (1, 2, 3, ...)
        movimientos: lista de tuplas (cilindro, accion)
                     Ej: [('A', '+'), ('B', '-')]
        """
        self.numero = numero
        self.movimientos = movimientos  # [(cilindro, accion), ...]
    
    def __repr__(self):
        return f"Fase {self.numero}: {self.movimientos}"


class InterpreteFuncion:
    
    def __init__(self, funcion: str):
        self.funcion = funcion.replace(" ", "")
        self.fases = []
        self.cilindros = set()
        self._interpretar()
    
    def _interpretar(self):
        """Interpreta la función y genera las fases"""
        fases_texto = self.funcion.split('/')
        
        for i, fase_texto in enumerate(fases_texto, 1):
            movimientos = []
            
            # Separar movimientos simultáneos
            movs_simultaneos = fase_texto.split(',')
            
            for mov in movs_simultaneos:
                cilindro = mov[0]
                accion = mov[1]
                movimientos.append((cilindro, accion))
                self.cilindros.add(cilindro)
            
            fase = Fase(i, movimientos)
            self.fases.append(fase)
    
    def obtener_cilindros_ordenados(self) -> list:
        """Retorna lista de cilindros en orden alfabético"""
        return sorted(self.cilindros)
    
    def obtener_estados_por_fase(self) -> dict:
        """
        Retorna diccionario con estados de cada cilindro en cada fase
        {
            'A': [False, True, True, False],  # False=Home, True=Work
            'B': [False, False, True, False],
            ...
        }
        Incluye estado inicial (fase 0)
        """
        cilindros = self.obtener_cilindros_ordenados()
        
        # Inicializar estados (fase 0: todos en Home)
        estados = {cilindro: [False] for cilindro in cilindros}
        
        # Procesar cada fase
        for fase in self.fases:
            for cilindro in cilindros:
                # Estado anterior
                estado_previo = estados[cilindro][-1]
                
                # Verificar si el cilindro se mueve en esta fase
                movimiento = None
                for mov_cilindro, mov_accion in fase.movimientos:
                    if mov_cilindro == cilindro:
                        movimiento = mov_accion
                        break
                
                if movimiento:
                    # Cambiar estado
                    nuevo_estado = (movimiento == '+')
                    estados[cilindro].append(nuevo_estado)
                else:
                    # Mantener estado anterior
                    estados[cilindro].append(estado_previo)
        
        return estados
    
    def obtener_cilindros_activos_por_fase(self) -> dict:
        """
        Retorna qué cilindros cambiaron de estado en cada fase
        {
            1: ['A'],
            2: ['B', 'C'],
            ...
        }
        """
        activos = {}
        
        for fase in self.fases:
            cilindros_fase = [cilindro for cilindro, _ in fase.movimientos]
            activos[fase.numero] = cilindros_fase
        
        return activos
    
    def obtener_descripcion_fase(self, numero_fase: int) -> str:
        """Retorna descripción textual de una fase"""
        if numero_fase == 0:
            return "Estado inicial: Todos los cilindros en posición Home (contraídos)"
        
        fase = self.fases[numero_fase - 1]
        
        descripciones = []
        for cilindro, accion in fase.movimientos:
            if accion == '+':
                descripciones.append(f"Cilindro {cilindro} se extiende (Home → Work)")
            else:
                descripciones.append(f"Cilindro {cilindro} se contrae (Work → Home)")
        
        return f"Fase {numero_fase}: " + ", ".join(descripciones)