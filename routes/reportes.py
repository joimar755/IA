from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generar_pdf_historial(historial, nombre_archivo="reporte.pdf"):
    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
    elementos = []
    styles = getSampleStyleSheet()

    estilo_usuario = styles['Normal']
    estilo_usuario.textColor = colors.blue
    estilo_bot = styles['Normal']
    estilo_bot.textColor = colors.green

    elementos.append(Paragraph("Reporte de Conversación", styles['Title']))
    elementos.append(Spacer(1, 20))

    for msg in historial:
        tipo = "Usuario" if msg.rol_id == 1 else "Bot"
        estilo = estilo_usuario if msg.rol_id == 1 else estilo_bot
        elementos.append(Paragraph(f"{tipo}: {msg.content}", estilo))
        elementos.append(Spacer(1, 10))

    doc.build(elementos)
    return nombre_archivo