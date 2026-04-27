"""
Generador de gráficos matplotlib
"""
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from utils import obtener_color_cilindro


class GeneradorGrafico:
    
    def __init__(self, interprete):
        self.interprete = interprete
        self.cilindros = interprete.obtener_cilindros_ordenados()
        self.estados = interprete.obtener_estados_por_fase()
        self.num_fases = len(interprete.fases)
    
    def generar_figura(self, hasta_fase: int = None) -> Figure:
        """
        Genera la figura de matplotlib
        hasta_fase: Si se especifica, solo dibuja hasta esa fase (para paso a paso)
        """
        if hasta_fase is None:
            hasta_fase = self.num_fases
        
        fig, ax = plt.subplots(figsize=(max(10, self.num_fases + 2), 6))
        
        # Ejes
        fases_x = list(range(0, hasta_fase + 1))  # Incluir fase 0
        
        # Dibujar línea para cada cilindro
        for i, cilindro in enumerate(self.cilindros):
            color = obtener_color_cilindro(i)
            estados_cilindro = self.estados[cilindro][:hasta_fase + 1]
            
            # Convertir True/False a 1/0
            estados_numericos = [1 if estado else 0 for estado in estados_cilindro]
            
            ax.plot(fases_x, estados_numericos, 
                   marker='o', 
                   linewidth=2.5, 
                   markersize=8,
                   label=f'Cilindro {cilindro}',
                   color=color)
        
        # Configuración del gráfico
        ax.set_xlabel('Fase', fontsize=12, fontweight='bold')
        ax.set_ylabel('Estado', fontsize=12, fontweight='bold')
        ax.set_title('Diagrama de Función de Transferencia', fontsize=14, fontweight='bold')
        
        # Configurar eje Y
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Home (SH)', 'Work (SW)'])
        ax.set_ylim(-0.1, 1.1)
        
        # Configurar eje X
        ax.set_xticks(fases_x)
        ax.set_xlim(-0.5, hasta_fase + 0.5)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Leyenda
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.tight_layout()
        
        return fig
    
    def guardar_png(self, ruta: str, hasta_fase: int = None):
        """Guarda el gráfico como PNG"""
        fig = self.generar_figura(hasta_fase)
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        plt.close(fig)