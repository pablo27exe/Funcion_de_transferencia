"""
Utilidades y constantes del sistema
"""

# Colores predefinidos para cilindros (RGB)
COLORES_CILINDROS = [
    (0.12, 0.47, 0.71),  # Azul
    (0.84, 0.15, 0.16),  # Rojo
    (0.17, 0.63, 0.17),  # Verde
    (0.58, 0.40, 0.74),  # Púrpura
    (0.55, 0.34, 0.29),  # Marrón
    (0.89, 0.47, 0.76),  # Rosa
    (0.50, 0.50, 0.50),  # Gris
    (0.74, 0.74, 0.13),  # Amarillo oscuro
    (0.09, 0.75, 0.81),  # Cyan
    (1.00, 0.50, 0.05),  # Naranja
]

def obtener_color_cilindro(index: int) -> tuple:
    """Retorna un color RGB para un cilindro basado en su índice"""
    return COLORES_CILINDROS[index % len(COLORES_CILINDROS)]

def obtener_nombre_estado(cilindro: str, extendido: bool) -> str:
    """
    Genera el nombre del estado de un cilindro
    cilindro: 'A', 'B', 'C', etc.
    extendido: True = Work (SWA), False = Home (SHA)
    """
    return f"SW{cilindro}" if extendido else f"SH{cilindro}"

def obtener_nombre_valvula(cilindro: str, extendido: bool) -> str:
    """
    Genera el nombre de la válvula de control
    cilindro: 'A', 'B', 'C', etc.
    extendido: True = YWA, False = YHA
    """
    return f"YW{cilindro}" if extendido else f"YH{cilindro}"