"""
Sistema de Diagramas de Función de Transferencia Neumática
Interfaz principal con Flet
"""
import flet as ft
import os
import tempfile
from pathlib import Path

from validador import ValidadorFuncion
from interprete import InterpreteFuncion
from generador_grafico import GeneradorGrafico
from generador_tabla import GeneradorTabla
from exportador import Exportador


class AplicacionNeumatica:
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Diagrama de Función de Transferencia Neumática"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.theme_mode = "light"
        self.page.padding = 20
        
        # Variables del sistema
        self.interprete = None
        self.generador_grafico = None
        self.generador_tabla = None
        self.fase_actual = 0  # Para modo paso a paso
        self.ruta_grafico_temp = None
        
        # Componentes UI
        self.txt_funcion = None
        self.btn_generar = None
        self.btn_exportar_pdf = None
        self.btn_exportar_png = None
        self.contenedor_resultado = None
        self.imagen_grafico = None
        self.tabla_estados = None
        self.contenedor_paso_a_paso = None
        self.txt_descripcion_fase = None
        self.btn_anterior = None
        self.btn_siguiente = None
        self.txt_fase_actual = None
        
        self._construir_ui()
    
    def _construir_ui(self):
        """Construye la interfaz de usuario"""
        
        # ========== SECCIÓN SUPERIOR: INPUT ==========
        self.txt_funcion = ft.TextField(
            label="Ingrese la función neumática",
            hint_text="Ejemplo: A+/B+/A-,B-",
            width=500,
            autofocus=True,
            on_submit=lambda e: self._generar_diagrama()
        )
        
        self.btn_generar = ft.ElevatedButton(
            text="Generar Diagrama",
            icon=ft.icons.PLAY_ARROW,
            on_click=lambda e: self._generar_diagrama(),
            style=ft.ButtonStyle(
                bgcolor={"": "#1f77b4", "hovered": "#1565c0"},
                color={"": "white"}
            )
        )
        
        seccion_input = ft.Container(
            content=ft.Column([
                ft.Text("Sistema de Diagramas Neumáticos", 
                       size=24, 
                       weight=ft.FontWeight.BOLD,
                       color="#1f77b4"),
                ft.Divider(height=20, color="transparent"),
                ft.Row([
                    self.txt_funcion,
                    self.btn_generar
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text(
                    "Formato: Letras mayúsculas (A-Z) + símbolos (+, -, /, ,)\n"
                    "+ = extender | - = contraer | / = separador de fases | , = movimientos simultáneos",
                    size=12,
                    color="grey",
                    text_align=ft.TextAlign.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            border=ft.border.all(1, "#cccccc"),
            border_radius=10,
            bgcolor="#f9f9f9"
        )
        
        # ========== SECCIÓN MEDIA: RESULTADOS ==========
        self.imagen_grafico = ft.Image(
            width=900,
            height=400,
            fit=ft.ImageFit.CONTAIN,
            visible=False
        )
        
        self.tabla_estados = ft.DataTable(
            columns=[],
            rows=[],
            border=ft.border.all(1, "black"),
            vertical_lines=ft.border.BorderSide(1, "black"),
            horizontal_lines=ft.border.BorderSide(1, "black"),
            visible=False
        )
        
        contenedor_tabla_scroll = ft.Container(
            content=self.tabla_estados,
            visible=False
        )
        
        self.contenedor_resultado = ft.Column([
            ft.Text("Gráfico de Estados", 
                   size=18, 
                   weight=ft.FontWeight.BOLD,
                   visible=False),
            self.imagen_grafico,
            ft.Divider(height=30, color="transparent"),
            ft.Text("Tabla de Estados y Válvulas", 
                   size=18, 
                   weight=ft.FontWeight.BOLD,
                   visible=False),
            ft.Container(
                content=contenedor_tabla_scroll,
                height=400,
                border=ft.border.all(1, "#cccccc"),
                border_radius=5
            )
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # ========== SECCIÓN PASO A PASO ==========
        self.txt_fase_actual = ft.Text("Fase: 0", size=16, weight=ft.FontWeight.BOLD)
        
        self.btn_anterior = ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            tooltip="Fase anterior",
            on_click=lambda e: self._cambiar_fase(-1),
            disabled=True
        )
        
        self.btn_siguiente = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD,
            tooltip="Siguiente fase",
            on_click=lambda e: self._cambiar_fase(1),
            disabled=True
        )
        
        self.txt_descripcion_fase = ft.Text(
            "", 
            size=14,
            text_align=ft.TextAlign.CENTER,
            width=800
        )
        
        self.contenedor_paso_a_paso = ft.Container(
            content=ft.Column([
                ft.Text("Modo Paso a Paso", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.btn_anterior,
                    self.txt_fase_actual,
                    self.btn_siguiente
                ], alignment=ft.MainAxisAlignment.CENTER),
                self.txt_descripcion_fase
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            visible=False,
            padding=15,
            border=ft.border.all(1, "#1f77b4"),
            border_radius=10,
            bgcolor="#e3f2fd"
        )
        
        # ========== SECCIÓN INFERIOR: EXPORTACIÓN ==========
        self.btn_exportar_pdf = ft.ElevatedButton(
            text="Exportar PDF",
            icon=ft.icons.PICTURE_AS_PDF,
            on_click=lambda e: self._exportar_pdf(),
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor={"": "#d32f2f", "hovered": "#c62828"},
                color={"": "white"}
            )
        )
        
        self.btn_exportar_png = ft.ElevatedButton(
            text="Exportar PNG",
            icon=ft.icons.IMAGE,
            on_click=lambda e: self._exportar_png(),
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor={"": "#388e3c", "hovered": "#2e7d32"},
                color={"": "white"}
            )
        )
        
        seccion_exportacion = ft.Row([
            self.btn_exportar_pdf,
            self.btn_exportar_png
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # ========== LAYOUT PRINCIPAL ==========
        self.page.add(
            ft.Column([
                seccion_input,
                ft.Divider(height=20, color="transparent"),
                self.contenedor_paso_a_paso,
                ft.Divider(height=20, color="transparent"),
                self.contenedor_resultado,
                ft.Divider(height=20, color="transparent"),
                seccion_exportacion
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )
    
    def _generar_diagrama(self):
        """Genera el diagrama completo"""
        funcion = self.txt_funcion.value
        
        if not funcion:
            self._mostrar_alerta("Error", "Debe ingresar una función", ft.icons.ERROR)
            return
        
        # Validar función
        es_valida, mensaje = ValidadorFuncion.validar(funcion)
        
        if not es_valida:
            self._mostrar_alerta("Error de Validación", mensaje, ft.icons.ERROR)
            return
        
        try:
            # Interpretar función
            self.interprete = InterpreteFuncion(funcion)
            self.generador_grafico = GeneradorGrafico(self.interprete)
            self.generador_tabla = GeneradorTabla(self.interprete)
            
            # Generar gráfico completo
            self._actualizar_grafico()
            
            # Generar tabla
            self._actualizar_tabla()
            
            # Activar modo paso a paso
            self.fase_actual = 0
            self._actualizar_paso_a_paso()
            
            # Activar botones de exportación
            self.btn_exportar_pdf.disabled = False
            self.btn_exportar_png.disabled = False
            
            # Mostrar elementos
            self.imagen_grafico.visible = True
            self.tabla_estados.visible = True
            self.contenedor_paso_a_paso.visible = True
            
            # Actualizar títulos
            for control in self.contenedor_resultado.controls:
                if isinstance(control, ft.Text):
                    control.visible = True
            
            self.page.update()
            
            self._mostrar_alerta(
                "Éxito", 
                f"Diagrama generado correctamente\n{len(self.interprete.cilindros)} cilindros, {len(self.interprete.fases)} fases", 
                ft.icons.CHECK_CIRCLE,
                ft.colors.GREEN
            )
            
        except Exception as ex:
            self._mostrar_alerta("Error", f"Error al generar diagrama: {str(ex)}", ft.icons.ERROR)
    
    def _actualizar_grafico(self, hasta_fase: int = None):
        """Actualiza la imagen del gráfico"""
        # Crear archivo temporal para el gráfico
        if self.ruta_grafico_temp:
            try:
                os.remove(self.ruta_grafico_temp)
            except:
                pass
        
        temp_dir = tempfile.gettempdir()
        self.ruta_grafico_temp = os.path.join(temp_dir, "grafico_neumatico_temp.png")
        
        # Generar y guardar gráfico
        self.generador_grafico.guardar_png(self.ruta_grafico_temp, hasta_fase)
        
        # Actualizar imagen en UI
        self.imagen_grafico.src = self.ruta_grafico_temp
        self.page.update()
    
    def _actualizar_tabla(self):
        """Actualiza la tabla de estados"""
        datos = self.generador_tabla.generar_datos_tabla()
        
        # Limpiar tabla
        self.tabla_estados.columns.clear()
        self.tabla_estados.rows.clear()
        
        # Crear columnas
        for header in datos['headers']:
            self.tabla_estados.columns.append(
                ft.DataColumn(
                    ft.Text(header, weight=ft.FontWeight.BOLD, size=14)
                )
            )
        
        # Crear filas
        for fila_data in datos['filas']:
            celdas = [
                ft.DataCell(
                    ft.Text(fila_data['nombre'], weight=ft.FontWeight.BOLD)
                )
            ]
            
            for celda_data in fila_data['valores']:
                # Color de fondo si está activa
                bgcolor = "#FFE4B5" if celda_data['activo'] and celda_data['valor'] else None
                
                celdas.append(
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                celda_data['valor'], 
                                size=12,
                                weight=ft.FontWeight.BOLD if celda_data['activo'] else ft.FontWeight.NORMAL
                            ),
                            bgcolor=bgcolor,
                            padding=5,
                            alignment=ft.alignment.center
                        )
                    )
                )
            
            self.tabla_estados.rows.append(ft.DataRow(cells=celdas))
        
        self.page.update()
    
    def _actualizar_paso_a_paso(self):
        """Actualiza la interfaz del modo paso a paso"""
        if not self.interprete:
            return
        
        # Actualizar texto de fase
        self.txt_fase_actual.value = f"Fase: {self.fase_actual}"
        
        # Actualizar descripción
        descripcion = self.interprete.obtener_descripcion_fase(self.fase_actual)
        self.txt_descripcion_fase.value = descripcion
        
        # Actualizar estado de botones
        self.btn_anterior.disabled = (self.fase_actual == 0)
        self.btn_siguiente.disabled = (self.fase_actual == len(self.interprete.fases))
        
        # Actualizar gráfico hasta la fase actual
        self._actualizar_grafico(hasta_fase=self.fase_actual if self.fase_actual > 0 else None)
        
        self.page.update()
    
    def _cambiar_fase(self, direccion: int):
        """Cambia la fase actual (±1)"""
        if not self.interprete:
            return
        
        nueva_fase = self.fase_actual + direccion
        
        # Validar límites
        if nueva_fase < 0:
            nueva_fase = 0
        elif nueva_fase > len(self.interprete.fases):
            nueva_fase = len(self.interprete.fases)
        
        self.fase_actual = nueva_fase
        self._actualizar_paso_a_paso()
    
    def _exportar_pdf(self):
        """Exporta el diagrama a PDF"""
        if not self.interprete:
            return
        
        try:
            # Diálogo para guardar archivo
            def guardar_pdf(e: ft.FilePickerResultEvent):
                if e.path:
                    ruta_pdf = e.path
                    if not ruta_pdf.endswith('.pdf'):
                        ruta_pdf += '.pdf'
                    
                    # Generar PDF
                    datos_tabla = self.generador_tabla.generar_datos_tabla()
                    Exportador.exportar_pdf(
                        ruta_pdf,
                        self.txt_funcion.value,
                        self.ruta_grafico_temp,
                        datos_tabla
                    )
                    
                    self._mostrar_alerta(
                        "Exportación Exitosa",
                        f"PDF guardado en:\n{ruta_pdf}",
                        ft.icons.CHECK_CIRCLE,
                        ft.colors.GREEN
                    )
            
            file_picker = ft.FilePicker(on_result=guardar_pdf)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            file_picker.save_file(
                dialog_title="Guardar PDF",
                file_name="diagrama_neumatico.pdf",
                allowed_extensions=["pdf"]
            )
            
        except Exception as ex:
            self._mostrar_alerta("Error", f"Error al exportar PDF: {str(ex)}", ft.icons.ERROR)
    
    def _exportar_png(self):
        """Exporta el gráfico a PNG"""
        if not self.generador_grafico:
            return
        
        try:
            # Diálogo para guardar archivo
            def guardar_png(e: ft.FilePickerResultEvent):
                if e.path:
                    ruta_png = e.path
                    if not ruta_png.endswith('.png'):
                        ruta_png += '.png'
                    
                    # Guardar PNG
                    self.generador_grafico.guardar_png(ruta_png)
                    
                    self._mostrar_alerta(
                        "Exportación Exitosa",
                        f"PNG guardado en:\n{ruta_png}",
                        ft.icons.CHECK_CIRCLE,
                        ft.colors.GREEN
                    )
            
            file_picker = ft.FilePicker(on_result=guardar_png)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            file_picker.save_file(
                dialog_title="Guardar PNG",
                file_name="grafico_neumatico.png",
                allowed_extensions=["png"]
            )
            
        except Exception as ex:
            self._mostrar_alerta("Error", f"Error al exportar PNG: {str(ex)}", ft.icons.ERROR)
    
    def _mostrar_alerta(self, titulo: str, mensaje: str, icono=ft.icons.INFO, color=None):
        """Muestra un diálogo de alerta"""
        def cerrar_dialogo(e):
            dialogo.open = False
            self.page.update()
        
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(icono, color=color),
                ft.Text(titulo)
            ]),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Aceptar", on_click=cerrar_dialogo)
            ]
        )
        
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()


def main(page: ft.Page):
    app = AplicacionNeumatica(page)


if __name__ == "__main__":
    ft.app(target=main)