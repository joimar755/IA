import smtplib
from email.message import EmailMessage

def enviar_pdf_correo(destinatario, archivo_pdf, asunto="Reporte de conversación"):
    remitente = "joimarjose19@gmail.com"
    password = "ygeg eadk ausy usiz"  # password de app si usas Gmail

    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = destinatario
    msg.set_content("Adjunto el reporte de la conversación solicitada.")

    with open(archivo_pdf, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=archivo_pdf)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(remitente, password)
        smtp.send_message(msg)