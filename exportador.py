"""
Exportador a PDF y PNG
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os


class Exportador:
    
    @staticmethod
    def exportar_pdf(ruta_pdf: str, funcion: str, ruta_imagen_grafico: str, datos_tabla: dict):
        """
        Exporta a PDF con función, gráfico y tabla
        """
        doc = SimpleDocTemplate(ruta_pdf, pagesize=landscape(A4))
        elementos = []
        
        styles = getSampleStyleSheet()
        
        # Estilo título
        style_titulo = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Estilo subtítulo
        style_subtitulo = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            alignment=TA_LEFT
        )
        
        # Título
        elementos.append(Paragraph("Diagrama de Función de Transferencia Neumática", style_titulo))
        
        # Función ingresada
        elementos.append(Paragraph(f"<b>Función:</b> {funcion}", styles['Normal']))
        elementos.append(Spacer(1, 0.5*cm))
        
        # Gráfico
        if os.path.exists(ruta_imagen_grafico):
            elementos.append(Paragraph("Gráfico de Estados", style_subtitulo))
            img = Image(ruta_imagen_grafico, width=18*cm, height=10*cm)
            elementos.append(img)
            elementos.append(Spacer(1, 0.5*cm))
        
        # Tabla de estados
        elementos.append(Paragraph("Tabla de Estados y Válvulas", style_subtitulo))
        
        # Construir datos para reportlab
        headers = datos_tabla['headers']
        filas_tabla = [headers]
        
        for fila_data in datos_tabla['filas']:
            fila_reportlab = [fila_data['nombre']]
            
            for celda in fila_data['valores']:
                fila_reportlab.append(celda['valor'])
            
            filas_tabla.append(fila_reportlab)
        
        # Crear tabla
        tabla = Table(filas_tabla, colWidths=[2.5*cm] + [1.5*cm]*(len(headers)-1))
        
        # Estilo de tabla
        style_tabla = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        # Resaltar celdas activas
        for i, fila_data in enumerate(datos_tabla['filas'], 1):
            for j, celda in enumerate(fila_data['valores'], 1):
                if celda['activo'] and celda['valor']:
                    style_tabla.add('BACKGROUND', (j, i), (j, i), colors.HexColor('#FFE4B5'))
        
        tabla.setStyle(style_tabla)
        elementos.append(tabla)
        
        # Generar PDF
        doc.build(elementos)