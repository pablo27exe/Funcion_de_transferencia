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
        self.activos = interprete.obtener_cilindros_activos_por_fase()
        self.num_fases = len(interprete.fases)
    
    def generar_figura(self, hasta_fase: int = None) -> Figure:
        """
        Genera la figura de matplotlib con separación vertical por cilindro
        hasta_fase: Si se especifica, solo dibuja hasta esa fase (para paso a paso)
        """
        if hasta_fase is None:
            hasta_fase = self.num_fases
        
        num_cilindros = len(self.cilindros)
        altura_por_cilindro = 2.5
        altura_total = num_cilindros * altura_por_cilindro + 1
        
        fig, ax = plt.subplots(figsize=(max(10, self.num_fases + 2), altura_total))
        
        # Ejes
        fases_x = list(range(0, hasta_fase + 1))
        x_labels = [f'Fase {i}' if i > 0 else 'Inicio' for i in fases_x]
        
        # Dibujar cada cilindro en su propio rango Y (INVERTIR orden para que A esté arriba)
        for idx, cilindro in enumerate(self.cilindros):
            # Invertir el índice: idx=0 (A) va arriba, idx=último va abajo
            y_base = (num_cilindros - 1 - idx) * altura_por_cilindro
            y_work = y_base + 1.8  # SWA (extendido)
            y_home = y_base + 0.2   # SHA (contraído)
            
            # Obtener estados (True=SWA, False=SHA)
            estados_cilindro = self.estados[cilindro][:hasta_fase + 1]
            
            # Convertir a valores Y
            valores_y = [y_work if estado else y_home for estado in estados_cilindro]
            
            # Dibujar línea del cilindro
            ax.plot(fases_x, valores_y, 
                   marker='o', 
                   linewidth=2.5, 
                   markersize=8,
                   color=obtener_color_cilindro(idx))
            
            # Etiqueta del cilindro a la izquierda
            y_media = (y_work + y_home) / 2
            ax.text(-0.3, y_media, f'{cilindro}', 
                   fontsize=11, fontweight='bold', ha='right', va='center')
            
            # Etiquetas SWA y SHA dentro del carril
            ax.text(-0.15, y_work, f'SW{cilindro}', fontsize=9, ha='right', va='bottom', color='green')
            ax.text(-0.15, y_home, f'SH{cilindro}', fontsize=9, ha='right', va='top', color='red')
            
            # Línea divisoria entre cilindros (excepto después del último)
            if idx < num_cilindros - 1:
                ax.axhline(y=y_base + altura_por_cilindro, color='gray', 
                          linestyle='--', linewidth=0.8, alpha=0.5)
        
        # Configuración del gráfico
        ax.set_xlabel('Fase', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cilindros', fontsize=12, fontweight='bold')
        ax.set_title('Diagrama de Función de Transferencia', fontsize=14, fontweight='bold')
        
        # Configurar eje X
        ax.set_xticks(fases_x)
        ax.set_xticklabels(x_labels, rotation=30, ha='right')
        ax.set_xlim(-0.8, hasta_fase + 0.5)
        
        # Configurar eje Y (ocultar valores numéricos)
        ax.set_ylim(-0.2, num_cilindros * altura_por_cilindro + 0.2)
        ax.set_yticks([])
        
        # Grid vertical solamente
        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        # SIN LEYENDA - eliminada la línea ax.legend()
        
        plt.tight_layout()
        
        return fig
    
    def guardar_png(self, ruta: str, hasta_fase: int = None):
        """Guarda el gráfico como PNG"""
        fig = self.generar_figura(hasta_fase)
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
        plt.close(fig)