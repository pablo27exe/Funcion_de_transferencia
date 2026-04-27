"""
Validador de funciones neumáticas
"""
import re

class ValidadorFuncion:
    
    @staticmethod
    def validar(funcion: str) -> tuple[bool, str]:
        """
        Valida la función ingresada
        Retorna: (es_valido, mensaje_error)
        """
        if not funcion or funcion.strip() == "":
            return False, "La función no puede estar vacía"
        
        # Eliminar espacios
        funcion = funcion.replace(" ", "")
        
        # Validar caracteres permitidos
        if not re.match(r'^[A-Z+\-/,]+$', funcion):
            return False, "Solo se permiten letras mayúsculas (A-Z) y símbolos: +, -, /, ,"
        
        # Validar que no contenga números
        if re.search(r'\d', funcion):
            return False, "No se permiten números en la función"
        
        # Dividir en fases
        fases = funcion.split('/')
        
        if len(fases) == 0:
            return False, "Debe haber al menos una fase"
        
        # Obtener todos los cilindros mencionados
        cilindros_usados = set()
        for fase in fases:
            # Extraer cilindros de la fase (pueden estar separados por comas)
            movimientos = fase.split(',')
            for mov in movimientos:
                # Extraer letra del cilindro (ignorar +/-)
                cilindro = mov.replace('+', '').replace('-', '')
                if cilindro:
                    cilindros_usados.add(cilindro)
        
        # Validar orden alfabético desde A
        if cilindros_usados:
            cilindros_ordenados = sorted(cilindros_usados)
            
            # Deben empezar desde A
            if cilindros_ordenados[0] != 'A':
                return False, "Los cilindros deben empezar desde 'A'"
            
            # Validar secuencia alfabética
            for i, cilindro in enumerate(cilindros_ordenados):
                esperado = chr(ord('A') + i)
                if cilindro != esperado:
                    return False, f"Falta el cilindro '{esperado}' en la secuencia alfabética"
        
        # Validar cada fase
        for i, fase in enumerate(fases, 1):
            if not fase:
                return False, f"La fase {i} está vacía"
            
            # Validar movimientos en la fase
            movimientos = fase.split(',')
            cilindros_en_fase = set()
            
            for mov in movimientos:
                if not mov:
                    return False, f"Movimiento vacío en fase {i}"
                
                # Debe tener formato: Letra + símbolo
                if not re.match(r'^[A-Z][+\-]$', mov):
                    return False, f"Formato inválido en fase {i}: '{mov}'. Debe ser formato: A+, B-, etc."
                
                cilindro = mov[0]
                
                # Validar que no se repita el mismo cilindro en la misma fase
                if cilindro in cilindros_en_fase:
                    return False, f"El cilindro '{cilindro}' aparece múltiples veces en la fase {i}"
                
                cilindros_en_fase.add(cilindro)
        
        # Validar movimientos consecutivos duplicados
        estados_cilindros = {}  # {cilindro: estado_actual (True=extendido, False=contraído)}
        
        # Inicializar todos en estado contraído (Home)
        for cilindro in cilindros_usados:
            estados_cilindros[cilindro] = False
        
        for i, fase in enumerate(fases, 1):
            movimientos = fase.split(',')
            
            for mov in movimientos:
                cilindro = mov[0]
                accion = mov[1]
                
                # Determinar nuevo estado
                nuevo_estado = (accion == '+')
                
                # Validar que no se intente hacer el mismo movimiento dos veces
                if estados_cilindros[cilindro] == nuevo_estado:
                    estado_texto = "extendido" if nuevo_estado else "contraído"
                    return False, f"Error en fase {i}: El cilindro '{cilindro}' ya está {estado_texto}"
                
                # Actualizar estado
                estados_cilindros[cilindro] = nuevo_estado
        
        return True, "Función válida"