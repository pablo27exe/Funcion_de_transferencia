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
        self.fase_actual = 0
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
            label="Ingrese la función de transferencia",
            hint_text="Ejemplo: A+/B+/A-,B-",
            width=500,
            autofocus=True,
            on_submit=lambda e: self._generar_diagrama()
        )
        
        self.btn_generar = ft.FilledButton(
            "Generar Diagrama",
            icon=ft.Icons.PLAY_ARROW,
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
            border=ft.Border.all(1, "#cccccc"),  # Cambiado ft.border.all → ft.Border.all
            border_radius=10,
            bgcolor="#f9f9f9"
        )
        
        # ========== SECCIÓN MEDIA: RESULTADOS ==========
        self.imagen_grafico = ft.Image(
            width=900,
            height=400,
            fit="contain",  # Cambiado ft.ImageFit.CONTAIN por "contain"
            visible=False,
            src=""
        )
        
        self.tabla_estados = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(""))],  # Columna temporal para evitar error
            rows=[],
            border=ft.Border.all(1, "black"),
            vertical_lines=ft.BorderSide(1, "black"),
            horizontal_lines=ft.BorderSide(1, "black"),
            visible=False
        )
        
        contenedor_tabla_scroll = ft.Container(
            content=self.tabla_estados,
            visible=True
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
                border=ft.Border.all(1, "#cccccc"), 
                border_radius=5
            )
        ], scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # ========== SECCIÓN PASO A PASO ==========
        self.txt_fase_actual = ft.Text("Fase: 0", size=16, weight=ft.FontWeight.BOLD)
        
        self.btn_anterior = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Fase anterior",
            on_click=lambda e: self._cambiar_fase(-1),
            disabled=True
        )
        
        self.btn_siguiente = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
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
            border=ft.Border.all(1, "#1f77b4"),  # Cambiado ft.border.all → ft.Border.all
            border_radius=10,
            bgcolor="#e3f2fd"
        )
        
        # ========== SECCIÓN INFERIOR: EXPORTACIÓN ==========
        self.btn_exportar_pdf = ft.FilledButton(
            "Exportar PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=lambda e: self._exportar_pdf(),
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor={"": "#d32f2f", "hovered": "#c62828"},
                color={"": "white"}
            )
        )
        
        self.btn_exportar_png = ft.FilledButton(
            "Exportar PNG",
            icon=ft.Icons.IMAGE,
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
        print("=== Botón Generar presionado ===")
        funcion = self.txt_funcion.value
        print(f"Función: '{funcion}'")
        
        if not funcion:
            print("Error: Función vacía")
            self._mostrar_alerta("Error", "Debe ingresar una función", ft.Icons.ERROR)
            return
        
        print("Validando función...")
        es_valida, mensaje = ValidadorFuncion.validar(funcion)
        print(f"¿Válida?: {es_valida}, Mensaje: {mensaje}")
        
        if not es_valida:
            self._mostrar_alerta("Error de Validación", mensaje, ft.Icons.ERROR)
            return
        
        try:
            print("Interpretando función...")
            self.interprete = InterpreteFuncion(funcion)
            print(f"Cilindros: {self.interprete.cilindros}, Fases: {len(self.interprete.fases)}")
            
            print("Generando gráfico...")
            self.generador_grafico = GeneradorGrafico(self.interprete)
            self.generador_tabla = GeneradorTabla(self.interprete)
            
            print("Actualizando gráfico...")
            self._actualizar_grafico()
            print("Gráfico actualizado")
            
            print("Actualizando tabla...")
            self._actualizar_tabla()
            print("Tabla actualizada")
            
            self.btn_exportar_pdf.disabled = False
            self.btn_exportar_png.disabled = False
            
            print("Haciendo visible...")
            self.imagen_grafico.visible = True
            self.tabla_estados.visible = True
            self.contenedor_paso_a_paso.visible = True
            
            for control in self.contenedor_resultado.controls:
                if isinstance(control, ft.Text):
                    control.visible = True
                    print(f"Texto visible: {control.value if hasattr(control, 'value') else 'texto'}")
            
            print("Actualizando página...")
            self.page.update()
            print("Página actualizada")
            
            #self._mostrar_alerta("Éxito", "Diagrama generado correctamente", ft.Icons.CHECK_CIRCLE, "green")
            
        except Exception as ex:
            print(f"ERROR: {ex}")
            import traceback
            traceback.print_exc()
            self._mostrar_alerta("Error", f"Error al generar diagrama: {str(ex)}", ft.Icons.ERROR)
    
    def _actualizar_grafico(self, hasta_fase: int = None):
        """Actualiza la imagen del gráfico"""
        import time
        import random
        
        if self.ruta_grafico_temp:
            try:
                os.remove(self.ruta_grafico_temp)
            except:
                pass
        
        temp_dir = tempfile.gettempdir()
        self.ruta_grafico_temp = os.path.join(temp_dir, f"grafico_neumatico_temp_{int(time.time())}_{random.randint(1000,9999)}.png")
        
        print(f"  Generando gráfico en: {self.ruta_grafico_temp}")
        self.generador_grafico.guardar_png(self.ruta_grafico_temp, hasta_fase)
        print(f"  Gráfico guardado, tamaño: {os.path.getsize(self.ruta_grafico_temp)} bytes")
        
        # Crear una nueva imagen en lugar de actualizar la existente
        nueva_imagen = ft.Image(
            src=self.ruta_grafico_temp,
            width=900,
            height=400,
            fit="contain",
            visible=True
        )
        
        # Reemplazar la imagen en el contenedor
        index = self.contenedor_resultado.controls.index(self.imagen_grafico)
        self.contenedor_resultado.controls[index] = nueva_imagen
        self.imagen_grafico = nueva_imagen
        
        # Forzar actualización
        self.page.update()
    
    def _actualizar_tabla(self):
        """Actualiza la tabla de estados"""
        datos = self.generador_tabla.generar_datos_tabla()
        
        self.tabla_estados.columns.clear()
        self.tabla_estados.rows.clear()
        
        for header in datos['headers']:
            self.tabla_estados.columns.append(
                ft.DataColumn(
                    ft.Text(header, weight=ft.FontWeight.BOLD, size=14)
                )
            )
        
        for fila_data in datos['filas']:
            celdas = [
                ft.DataCell(
                    ft.Text(fila_data['nombre'], weight=ft.FontWeight.BOLD)
                )
            ]
            
            for celda_data in fila_data['valores']:

                celdas.append(
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                celda_data['valor'], 
                                size=12,
                                weight=ft.FontWeight.BOLD if celda_data['activo'] else ft.FontWeight.NORMAL
                            ),

                            padding=5,
                            alignment=ft.Alignment(0, 0)
                        )
                    )
                )
            
            self.tabla_estados.rows.append(ft.DataRow(cells=celdas))
        
        self.page.update()
    
    def _actualizar_paso_a_paso(self):
        """Actualiza la interfaz del modo paso a paso"""
        if not self.interprete:
            return
        
        self.txt_fase_actual.value = f"Fase: {self.fase_actual}"
        
        descripcion = self.interprete.obtener_descripcion_fase(self.fase_actual)
        self.txt_descripcion_fase.value = descripcion
        
        self.btn_anterior.disabled = (self.fase_actual == 0)
        self.btn_siguiente.disabled = (self.fase_actual == len(self.interprete.fases))
        
        self._actualizar_grafico(hasta_fase=self.fase_actual if self.fase_actual > 0 else None)
        
        self.page.update()
    
    def _cambiar_fase(self, direccion: int):
        """Cambia la fase actual (±1)"""
        if not self.interprete:
            return
        
        nueva_fase = self.fase_actual + direccion
        
        if nueva_fase < 0:
            nueva_fase = 0
        elif nueva_fase > len(self.interprete.fases):
            nueva_fase = len(self.interprete.fases)
        
        self.fase_actual = nueva_fase
        self._actualizar_paso_a_paso()
    
    def _exportar_pdf(self):
        """Exporta el diagrama a PDF directamente en Descargas"""
        import os
        from pathlib import Path
        
        if not self.interprete:
            self._mostrar_alerta("Error", "Primero genera un diagrama", ft.Icons.ERROR)
            return
        
        # Verificar que el gráfico existe
        if not self.ruta_grafico_temp or not os.path.exists(self.ruta_grafico_temp):
            self._mostrar_alerta("Error", "No hay gráfico generado", ft.Icons.ERROR)
            return
        
        try:
            # Carpeta de Descargas
            descargas = Path.home() / "Downloads" / "Descargas"
            if not descargas.exists():
                descargas = Path.home() / "Downloads"
            if not descargas.exists():
                descargas = Path.home() / "Descargas"
            
            # Crear nombre de archivo con timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_pdf = descargas / f"diagrama_neumatico_{timestamp}.pdf"
            
            # Generar datos de tabla
            datos_tabla = self.generador_tabla.generar_datos_tabla()
            
            # Exportar
            Exportador.exportar_pdf(
                str(ruta_pdf),
                self.txt_funcion.value,
                self.ruta_grafico_temp,
                datos_tabla
            )
            
            self._mostrar_alerta(
                "Exportación Exitosa",
                f"PDF guardado en:\n{ruta_pdf}",
                ft.Icons.CHECK_CIRCLE,
                "green"
            )
            
        except Exception as ex:
            print(f"ERROR: {ex}")
            import traceback
            traceback.print_exc()
            self._mostrar_alerta("Error", f"Error al exportar PDF: {str(ex)}", ft.Icons.ERROR)


    def _exportar_png(self):
        """Exporta el gráfico a PNG directamente en Descargas"""
        import os
        from pathlib import Path
        
        if not self.generador_grafico:
            self._mostrar_alerta("Error", "Primero genera un diagrama", ft.Icons.ERROR)
            return
        
        if not self.ruta_grafico_temp or not os.path.exists(self.ruta_grafico_temp):
            self._mostrar_alerta("Error", "No hay gráfico generado", ft.Icons.ERROR)
            return
        
        try:
            # Carpeta de Descargas
            descargas = Path.home() / "Downloads" / "Descargas"
            if not descargas.exists():
                descargas = Path.home() / "Downloads"
            if not descargas.exists():
                descargas = Path.home() / "Descargas"
            
            # Crear nombre de archivo con timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_png = descargas / f"grafico_neumatico_{timestamp}.png"
            
            # Copiar el gráfico temporal o generarlo directamente
            import shutil
            shutil.copy2(self.ruta_grafico_temp, ruta_png)
            
            self._mostrar_alerta(
                "Exportación Exitosa",
                f"PNG guardado en:\n{ruta_png}",
                ft.Icons.CHECK_CIRCLE,
                "green"
            )
            
        except Exception as ex:
            print(f"ERROR: {ex}")
            import traceback
            traceback.print_exc()
            self._mostrar_alerta("Error", f"Error al exportar PNG: {str(ex)}", ft.Icons.ERROR)
    
    def _mostrar_alerta(self, titulo: str, mensaje: str, icono=ft.Icons.INFO, color=None):
        """Muestra un diálogo de alerta"""
        
        color_icono = color if color else "blue"
        
        # Variable para guardar la referencia al diálogo
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(icono, color=color_icono),
                ft.Text(titulo, weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda e: _cerrar())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: _cerrar(),  # También cerrar si se clic fuera
        )
        
        def _cerrar():
            dialogo.open = False
            # Esperar un momento antes de remover
            self.page.update()
            # Remover del overlay después de un breve delay
            import threading
            threading.Timer(0.1, lambda: self._remover_dialogo(dialogo)).start()
        
        self.page.overlay.append(dialogo)
        dialogo.open = True
        self.page.update()

    def _remover_dialogo(self, dialogo):
        """Remueve el diálogo del overlay"""
        try:
            if dialogo in self.page.overlay:
                self.page.overlay.remove(dialogo)
                self.page.update()
        except:
            pass

def main(page: ft.Page):
    app = AplicacionNeumatica(page)


if __name__ == "__main__":
    ft.app(target=main) 